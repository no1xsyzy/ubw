import asyncio
import json
import logging
import ssl as ssl_
from typing import Literal

import aiohttp
import yarl
from pydantic import Field

from ._wsbase import *
from .bilibili import BilibiliCookieClient, BilibiliApiError, USER_AGENT
from ..models.bilibili import Host

logger = logging.getLogger('ubw.clients.wsweb')


class WSWebCookieClient(WSMessageParserMixin, ClientABC):
    clientc: Literal['wsweb'] = 'wsweb'
    bilibili_client: BilibiliCookieClient = Field(default_factory=BilibiliCookieClient)

    # defaults
    heartbeat_interval: int = 30

    # dynamic
    _host_server_list: list[Host] | None = None
    _host_server_token: str | None = None
    _buvid3: str | None = None
    _uid: int | None = None

    # runtime stuff
    _task: asyncio.Task | None = None
    _websocket: aiohttp.ClientWebSocketResponse | None = None
    _heartbeat_timer_task: asyncio.Task | None = None
    _session: aiohttp.ClientSession | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None

    def start(self):
        if self.is_running:
            logger.warning('room=%s client is running, cannot start() again', self.room_id)
            return

        self._session = self.bilibili_client.make_session()
        # self._session = self.bilibili_client.make_session(timeout=aiohttp.ClientTimeout(total=10))
        self.__dict__['_task'] = asyncio.create_task(self.main())

    def stop(self):
        if not self.is_running:
            logger.warning('room=%s client is stopped, cannot stop() again', self.room_id)
            return

        self._task.cancel('stop')

    async def stop_and_close(self):
        try:
            if self.is_running:
                self.stop()
                await self.join()
        finally:
            await self.close()

    async def join(self):
        if not self.is_running:
            logger.warning('room=%s client is stopped, cannot join()', self.room_id)
            return

        logger.debug('room=%s joining', self.room_id)
        await asyncio.shield(self._task)

    async def close(self):
        if self.is_running:
            logger.warning('room=%s is calling close(), but client is running', self.room_id)
        await self._session.close()

    async def _init_room(self):
        res = True
        # if not await self._try_init_from_environ() and not await self._init_buvid():
        #     res = False
        cookies = self._session.cookie_jar.filter_cookies(yarl.URL('https://www.bilibili.com/'))
        self._uid = int(cookies['DedeUserID'].value)
        self._buvid3 = cookies['buvid3'].value
        if not await self._init_host_server():
            res = False
        return res

    async def _init_host_server(self):
        logger.debug('room=%d _init_host_server() invoked', self.room_id)
        try:
            server = await self.bilibili_client.get_danmaku_server(self.room_id)
            # server: bilibili.DanmuInfo = await bilibili.get_danmaku_server(self.room_id, session=self._session)
            self._host_server_list = server.host_list
            self._host_server_token = server.token
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError, BilibiliApiError):
            logger.exception('room=%d _init_host_server() failed:', self.room_id)
            self._host_server_list = [Host(
                host='broadcastlv.chat.bilibili.com', port=2243, wss_port=443, ws_port=2244
            )]
            self._host_server_token = None
            return False
        return True

    @staticmethod
    def _make_packet(data: dict, operation: int) -> bytes:
        """
        创建一个要发送给服务器的包

        :param data: 包体JSON数据
        :param operation: 操作码，见Operation
        :return: 整个包的数据
        """
        body = json.dumps(data).encode('utf-8')
        header = HEADER_STRUCT.pack(*HeaderTuple(
            pack_len=HEADER_STRUCT.size + len(body),
            raw_header_size=HEADER_STRUCT.size,
            ver=1,
            operation=operation,
            seq_id=1
        ))
        return header + body

    async def main(self):
        try:
            await self._network_coroutine()
        except Exception as e:  # noqa
            logger.exception(f'room={self.room_id} WSWebClient._network_coroutine() finished with exception:')
        finally:
            logger.info(f'room={self.room_id} WSWebClient._network_coroutine() finalized')
            self._task = None

    async def _network_coroutine(self):
        # 如果之前未初始化则初始化
        if self._host_server_token is None:
            if not await self._init_room():
                raise InitError('init_room() failed')

        retry_count = 0
        while True:
            try:
                # 连接
                host_server = self._host_server_list[retry_count % len(self._host_server_list)]
                async with self._session.ws_connect(
                        f"wss://{host_server.host}:{host_server.wss_port}/sub",
                        headers={'User-Agent': USER_AGENT},
                        receive_timeout=self.heartbeat_interval + 5,
                ) as websocket:
                    self._websocket = websocket
                    await self._on_ws_connect()

                    # 处理消息
                    message: aiohttp.WSMessage
                    async for message in websocket:
                        await self._on_ws_message(message)
                        # 至少成功处理1条消息
                        retry_count = 0

            except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
                # 掉线重连
                pass
            except AuthError:
                # 认证失败了，应该重新获取token再重连
                logger.exception('room=%d auth failed, trying init_room() again', self.room_id)
                if not await self._init_room():
                    raise InitError('init_room() failed')
            except ssl_.SSLError:
                logger.error('room=%d a SSLError happened, cannot reconnect', self.room_id)
                raise
            finally:
                self._websocket = None
                await self._on_ws_close()

            # 准备重连
            retry_count += 1
            logger.warning('room=%d is reconnecting, retry_count=%d', self.room_id, retry_count)
            await asyncio.sleep(1)

    async def _on_ws_connect(self):
        """
        websocket连接成功
        """
        await self._send_auth()
        self._heartbeat_timer_task = asyncio.create_task(self._heartbeat_timer())

    async def _on_ws_close(self):
        """
        websocket连接断开
        """
        if self._heartbeat_timer_task is not None:
            self._heartbeat_timer_task.cancel('ws close')
            self._heartbeat_timer_task = None

    async def _send_auth(self):
        """
        发送认证包
        """
        auth_params = {
            'uid': 0,
            'roomid': self.room_id,
            'protover': 3,
            'platform': 'web',
            'type': 2
        }
        if self._host_server_token is not None:
            auth_params['key'] = self._host_server_token
        if self._buvid3 is not None:
            auth_params['buvid'] = self._buvid3

        logger.debug(f"auth_params=%s", auth_params)

        await self._websocket.send_bytes(self._make_packet(auth_params, Operation.AUTH))

    async def _heartbeat_timer(self):
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            if self._websocket is None or self._websocket.closed:
                self._heartbeat_timer_task = None
                return
            asyncio.create_task(self._send_heartbeat())

    async def _send_heartbeat(self):
        """
        发送心跳包
        """
        if self._websocket is None or self._websocket.closed:
            return

        try:
            await self._websocket.send_bytes(self._make_packet({}, Operation.HEARTBEAT))
        except (ConnectionResetError, aiohttp.ClientConnectionError) as e:
            logger.warning('room=%d _send_heartbeat() failed: %r', self.room_id, e)
        except Exception:  # noqa
            logger.exception('room=%d _send_heartbeat() failed:', self.room_id)
