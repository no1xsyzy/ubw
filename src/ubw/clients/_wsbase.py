import abc
import asyncio
import json
import logging
import struct
from functools import partial
from typing import AsyncGenerator, Any

import aiohttp
import brotli

from ._livebase import *

__all__ = (
    # types
    'HandlerInterface',
    'LiveClientABC',
    'HeaderTuple',
    'WSMessageParserMixin',
    'Literal',

    # exceptions
    'InitError',
    'AuthError',

    # enums
    'ProtoVer',
    'Operation',
    'AuthReplyCode',

    # consts
    'DEFAULT_DANMAKU_SERVER_LIST',
    'HEADER_STRUCT',
)

logger = logging.getLogger('wsclient')


class YieldRestBytes(BaseException):
    pass


class WSMessageParserMixin(LiveClientABC, abc.ABC):
    async def _on_ws_message(self, message: aiohttp.WSMessage):
        """
        收到websocket消息

        :param message: websocket消息
        """
        if message.type != aiohttp.WSMsgType.BINARY:  # pragma: no cover
            logger.warning('room=%d unknown websocket message type=%s, data=%s', self.room_id,
                           message.type, message.data)
            return

        try:
            await self._parse_ws_message(message.data)
        except (asyncio.CancelledError, AuthError):  # pragma: no cover
            # 正常停止、认证失败，让外层处理
            raise
        except Exception:  # noqa
            logger.exception('room=%d _parse_ws_message() error:', self.room_id)

    async def _iter_pack(self, pack: bytes) -> AsyncGenerator[tuple[HeaderTuple | None,
                                                                    Any | bytes | tuple[bytes, bytes]], Any]:
        offset = 0
        try:
            while offset < len(pack):
                try:
                    header = HeaderTuple(*HEADER_STRUCT.unpack_from(pack, offset))
                except struct.error:  # pragma: no cover, should not happen
                    logger.exception(f'room={self.room_id} parsing header failed\n{offset = }\n{pack[offset:] = }')
                    return
                body: bytes = pack[offset + header.raw_header_size:offset + header.pack_len]
                offset += header.pack_len
                if header.ver == ProtoVer.BROTLI:
                    body_decoded = await asyncio.to_thread(partial(brotli.decompress, body))
                    async for header, body in self._iter_pack(body_decoded):
                        yield header, body
                elif header.ver == ProtoVer.NORMAL:
                    if body:
                        try:
                            yield header, json.loads(body.decode('utf-8'))
                        except Exception as e:  # pragma: no cover, not reachable
                            logger.error(f'room={self.room_id} ProtoVer.NORMAL json error\n{body = }\n{e = }')
                            yield header, body
                    else:
                        yield header, body
                elif header.ver == ProtoVer.HEARTBEAT:
                    popularity = int.from_bytes(body, 'big')
                    extra = body[offset:]
                    offset = len(pack)
                    if extra not in [b'{}', b'']:
                        logger.warning('unexpected extra=%s header=%s popularity=%s body=%s',
                                       repr(extra), repr(header), repr(popularity), repr(body))
                    yield header, (body, extra)
                else:
                    logger.warning('room=%d unknown protocol version=%d, header=%s, body=%s', self.room_id,
                                   header.ver, header, body)
        except YieldRestBytes:
            yield None, pack[offset:]

    async def _parse_ws_message(self, data: bytes):
        """
        解析websocket消息

        :param data: websocket消息数据
        """
        it = self._iter_pack(data)
        async for header, body in it:
            if header.operation == Operation.SEND_MSG_REPLY:
                await self._handle_command(body)
            elif header.operation == Operation.AUTH_REPLY:
                assert body[1] == b''
                body = body[0]
                body = json.loads(body.decode('utf-8'))
                if body['code'] != AuthReplyCode.OK:
                    raise AuthError(f"auth reply error, {body=}")
            elif header.operation == Operation.HEARTBEAT_REPLY:
                popularity = int.from_bytes(body[0], 'big')
                extra = body[1].decode()
                await self._handle_command({
                    'cmd': 'X_UBW_HEARTBEAT',
                    'popularity': popularity,
                    'client_heartbeat_content': extra,
                })
            else:  # pragma: no cover, should not happen
                # 未知消息
                logger.warning('room=%d unknown message operation=%d, header=%s, body=%s', self.room_id,
                               header.operation, header, body)

    async def _handle_command(self, command: dict):
        """
        解析并处理业务消息

        :param command: 业务消息
        """
        # 外部代码可能不能正常处理取消，所以这里加shield
        results = await asyncio.shield(
            asyncio.gather(
                *(handler.handle(self, command) for handler in self._handlers),
                return_exceptions=True
            )
        )
        for res in results:
            if isinstance(res, Exception):
                logger.exception('room=%d _handle_command() failed, command=%s', self.room_id, command, exc_info=res)
