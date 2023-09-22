# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import struct
import zlib

import brotli

import bilibili
from ._base import *

__all__ = ('TcpClient',)

logger = logging.getLogger('tcpclient')

HEADER_STRUCT = struct.Struct('>I2H2I')


class TcpClient(ClientABC):
    def __init__(self, hosts, room_id, token):
        super().__init__()
        self.hosts = hosts  # type: list[bilibili.models.Host]
        self.room_id = room_id  # type: int
        self.token = token  # type: str
        self._handlers = []  # type: list[HandlerInterface]
        self._task = None  # type: asyncio.Task | None
        self._heart = None  # type: asyncio.Task | None
        self._reader = None  # type: asyncio.StreamReader | None
        self._writer = None  # type: asyncio.StreamWriter | None
        self._heartbeat_interval = 30  # type: int

    @classmethod
    async def room(cls, room_id):
        c: bilibili.DanmuInfo = await bilibili.get_danmaku_server(room_id)
        return cls(c.host_list, room_id, c.token)

    async def _init_room(self):
        c: bilibili.DanmuInfo = await bilibili.get_danmaku_server(self.room_id)
        self.hosts = c.host_list
        self.token = c.token

    def add_handler(self, handler):
        if handler not in self._handlers:
            self._handlers.append(handler)

    def start(self):
        if self._task is not None:
            logger.warning('room=%s client is running, cannot start() again', self.room_id)
        self._task = asyncio.create_task(self._network_coroutine())
        return self._task

    async def _network_coroutine(self):
        try:
            retry_count = 0
            while True:
                try:
                    host = self.hosts[retry_count % len(self.hosts)]
                    self._reader, self._writer = await asyncio.open_connection(host.host, host.port)
                    await self._join_room()
                    while header := await self._read_header():
                        body = await self._reader.readexactly(header.pack_len - HEADER_STRUCT.size)
                        # print("raw", body)
                        await self._proc_pack(header, body)
                except asyncio.exceptions.IncompleteReadError:
                    # 断线重连？
                    try:
                        self._writer.close()
                    except Exception:
                        pass
                    self._reader = self._writer = None
                except AuthError:
                    # 认证失败了，应该重新获取token再重连
                    logger.info('room=%d auth failed, trying init_room() again', self.room_id)
                    await self._init_room()
        except Exception as e:  # noqa
            logger.exception('room=%s _network_coroutine() finished with exception:', self.room_id)
        finally:
            self._task = None

    async def _proc_pack(self, header: HeaderTuple, body: bytes):
        if header.ver == ProtoVer.DEFLATE:
            await self._proc_multi_pack(await asyncio.to_thread(zlib.decompress, body))
        elif header.ver == ProtoVer.BROTLI:
            await self._proc_multi_pack(await asyncio.to_thread(brotli.decompress, body))
        elif header.ver == ProtoVer.NORMAL:
            print(Operation(header.operation), body)
            if len(body) == 0:
                d = None
            else:
                d = json.loads(body.decode('utf-8'))
            await self._proc_cmd(header, d)

    async def _proc_cmd(self, header: HeaderTuple, d: dict):
        if header.operation == Operation.AUTH_REPLY:
            if d['code'] != AuthReplyCode.OK:
                raise AuthError(f"auth reply error, code={d['code']}, body={d}")
        elif header.operation == Operation.SEND_MSG_REPLY:
            try:
                for handler in self._handlers:
                    await handler.handle(self, d)
            except Exception as e:
                logger.exception('room=%d _proc_cmd() failed, command=%s', self.room_id, d, exc_info=e)

    async def _proc_multi_pack(self, pack: bytes):
        offset = 0
        while offset < len(pack) and (header := HeaderTuple(*HEADER_STRUCT.unpack_from(pack, offset))):
            await self._proc_pack(header, pack[offset + HEADER_STRUCT.size:offset + header.pack_len])
            offset += header.pack_len

    async def _read_header(self):
        assert self._reader is not None
        return HeaderTuple(*HEADER_STRUCT.unpack(await self._reader.readexactly(HEADER_STRUCT.size)))

    async def _join_room(self):
        payload = json.dumps({'roomid': self.room_id, 'uid': 0, 'protover': 3, 'key': self.token, 'type': 2})
        await self._send(Operation.AUTH, payload)

    async def _send_heartbeat(self):
        await self._send(Operation.HEARTBEAT, '{}')

    async def _send_heartbeats(self):
        while True:
            await asyncio.sleep(self._heartbeat_interval)
            await self._send_heartbeat()

    async def _send(self, operation: int, payload: str):
        body = payload.encode('utf-8')
        assert isinstance(self._writer, asyncio.StreamWriter)
        self._writer.write(HEADER_STRUCT.pack(*HeaderTuple(
            pack_len=HEADER_STRUCT.size + len(body),
            raw_header_size=HEADER_STRUCT.size,
            ver=1,
            operation=operation,
            seq_id=1,
        )) + body)
        await self._writer.drain()

    async def join(self):
        if self._task is not None:
            await asyncio.shield(self._task)

    def stop(self):
        if self._task is not None:
            self._task.cancel("stop")
            self._writer.close()
            self._reader = self._writer = self._task = None

    async def close(self):
        pass

    async def stop_and_close(self):
        task = self._task
        if task:
            self.stop()
            await task
        await self.close()


class DummyClient(ClientABC):
    """测试用，可手动发送也可发送随机信息"""
    MESSAGES = [
        "Lorem ipsum dolor sit amet",
        "The quick brown fox jumps over the lazy dog",
        "我能吞下玻璃而不伤身体",
        "私はガラスを食べられます。それは私を傷つけません。",
    ]
    INTERVAL = (1, 0.7)

    def __init__(self):
        super().__init__()
        self._task = None

    def start(self):
        self._task = True

    async def _random_command(self):
        import random
        while True:
            for handler in self._handlers:
                await handler.handle(self, self._create_command())
            await asyncio.sleep(random.normalvariate(*self.INTERVAL))

    def _create_command(self):
        return {"cmd": "DANMU_MSG"}

    async def _replay_raw(self, fn):
        import random
        with open(fn, 'r') as fp:
            d = json.load(fp)
        for j in d['_default'].values():
            if 'cmd' in j:
                for handler in self._handlers:
                    await handler.handle(self, j)
                await asyncio.sleep(random.normalvariate(*self.INTERVAL))

    async def stop_and_close(self):
        task = self._task
        if task:
            self.stop()
        await self.close()

    async def close(self):
        pass

    def stop(self):
        self._task = False

    async def join(self):
        await asyncio.shield(self._task)
