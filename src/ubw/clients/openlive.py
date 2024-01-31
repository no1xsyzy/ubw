import abc
import asyncio
import json as json_
import logging
import uuid
from datetime import datetime
from typing import Optional, Literal, Annotated

import aiohttp
from pydantic import BaseModel
from pydantic import Field

from ._livebase import *
from ._wsbase import HEADER_STRUCT, WSMessageParserMixin
from .bilibili import BilibiliApiError, USER_AGENT
from ..models import Response

logger = logging.getLogger('open_live_client')


class GameInfo(BaseModel):
    game_id: str
    """场次id,心跳key(心跳保持20s-60s)调用一次,超过60s无心跳自动关闭,长连停止推送消息"""


class WebsocketInfo(BaseModel):
    auth_body: str
    """长连使用的请求json体 第三方无需关注内容,建立长连时使用即可"""
    wss_link: list[str]
    """wss 长连地址"""


class AnchorInfo(BaseModel):
    room_id: int
    """主播房间号"""
    uname: str
    """主播昵称"""
    uface: str
    """主播头像"""
    uid: int
    """主播uid"""


class StartData(BaseModel):
    game_info: GameInfo
    websocket_info: WebsocketInfo
    anchor_info: AnchorInfo


class AppABC(BaseModel, abc.ABC):
    app_type: str

    @abc.abstractmethod
    async def start(self, session, room_owner_auth_code): ...

    @abc.abstractmethod
    async def end(self, session): ...

    @abc.abstractmethod
    async def heartbeat(self, session): ...


class CommonApp(AppABC, abc.ABC):
    api_host: str = "https://live-open.biliapi.com"
    app_id: int

    _start_data = None

    @abc.abstractmethod
    async def _sign_bytes(self, b):
        ...

    async def _req(self, session, endpoint: str, data: bytes | None = None, *, json: dict | None = None):
        if data is None:
            data = json_.dumps(json).encode('utf-8')
        headers = await self._sign_bytes(data)
        headers['content-type'] = headers['accept'] = 'application/json'
        return session.post(self.api_host + endpoint, headers=headers, data=data)

    async def start(self, session, room_owner_auth_code):
        if self._start_data is not None:
            logger.warning('_app_start() after initiated')
            return self._start_data
        async with self._req(session, '/v2/app/start',
                             json={'code': room_owner_auth_code, 'app_id': self.app_id}) as res:
            j: Response[StartData] = Response[StartData].model_validate(await res.json())
            if j.code != 0:
                raise BilibiliApiError(j.code, j.message)
            self._start_data = j.data
            return self._start_data

    async def end(self, session):
        if self._start_data is None:
            logger.warning('_app_end() before initiated')
            return
        async with self._req(session, '/v2/app/end',
                             json={'app_id': self.app_id, 'game_id': self._start_data.game_info.game_id}) as res:
            j: Response[dict] = Response[dict].model_validate(await res.json())
            if j.code != 0:
                raise BilibiliApiError(j.code, j.message)
            self._start_data = None

    async def heartbeat(self, session):
        if self._start_data is None:
            logger.warning('_app_heartbeat() before initiated')
            return
        async with self._req(session, '/v2/app/heartbeat',
                             json={'game_id': self._start_data.game_info.game_id}) as res:
            j: Response[dict] = Response[dict].model_validate(await res.json())
            if j.code != 0:
                raise BilibiliApiError(j.code, j.message)


class AppDirect(CommonApp):
    app_type: Literal['direct'] = 'direct'
    access_key_id: str
    access_key_secret: str

    async def _sign_bytes(self, b):
        import hashlib
        import hmac
        content_md5 = hashlib.md5(b).hexdigest()
        nonce = uuid.uuid4()
        time = int(datetime.now().timestamp())
        header = (
            f"x-bili-accesskeyid:{self.access_key_id}\n"
            f"x-bili-content-md5:{content_md5}\n"
            "x-bili-signature-method:HMAC-SHA256\n"
            f"x-bili-signature-nonce:{nonce}\n"
            "x-bili-signature-version:1.0\n"
            f"x-bili-timestamp:{time}"
        )

        signature = hmac.new(self.access_key_secret.encode(), header.encode(), digestmod=hashlib.sha256).hexdigest()

        return {
            'Authorization': signature,
            'x-bili-accesskeyid': self.access_key_secret,
            'x-bili-content-md5': content_md5,
            'x-bili-signature-method': "HMAC-SHA256",
            'x-bili-signature-nonce': nonce,
            'x-bili-signature-version': "1.0",
            'x-bili-timestamp': time,
        }


class CEVEApp(CommonApp):
    app_type: Literal['ceve'] = 'ceve'

    async def _sign_bytes(self, b):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://bopen.ceve-market.org/sign', data=b) as res:
                return res.json()


class OpenLiveClient(WSMessageParserMixin, LiveClientABC):
    """Experimental. Require more works, such as using third party access key."""
    clientc: Literal['open_live'] = 'open_live'

    app: Annotated[AppDirect | CEVEApp, Field(discriminator='app_type')]

    room_owner_auth_code: str

    game_heartbeat_interval: int = 20
    ws_heartbeat_interval: int = 30

    _session: Optional[aiohttp.ClientSession] = None
    _game_heartbeat_task: asyncio.Task | None = None
    _ws_heartbeat_task: asyncio.Task | None = None
    _start_data: StartData | None = None
    _ws: aiohttp.ClientWebSocketResponse | None = None

    def start(self):
        if self.is_running:
            logger.warning('start() while running')
            return
        self.__dict__['_task'] = asyncio.create_task(self._run())

    async def join(self):
        if not self.is_running:
            logger.warning('join() while stopped')
            return
        await asyncio.shield(self._task)

    def stop(self):
        if not self.is_running:
            logger.warning('stop() while stopped')
            return
        self._task.cancel()

    async def close(self):
        if self.is_running:
            logger.warning('close() while running')
        if self._own_session:
            await self._session.close()

    @property
    def room_id(self):
        if self._start_data is None:
            return 0
        return self._start_data.anchor_info.room_id

    @property
    def room_owner_uid(self):
        if self._start_data is None:
            return 0
        return self._start_data.anchor_info.uid

    async def _run(self):
        try:
            await self._app_start()
            self._game_heartbeat_task = asyncio.create_task(self._game_heart())
            retry_count = 0
            while True:
                try:
                    # 连接
                    host_servers = self._start_data.websocket_info.wss_link
                    host_server = host_servers[retry_count % len(host_servers)]
                    async with self._session.ws_connect(
                            host_server,
                            headers={'User-Agent': USER_AGENT},
                            receive_timeout=self.ws_heartbeat_interval + 5,
                    ) as websocket:
                        self._ws = websocket
                        await self._send_auth()
                        self._ws_heartbeat_task = asyncio.create_task(self._ws_heart())

                        # 处理消息
                        message: aiohttp.WSMessage
                        async for message in websocket:
                            await self._on_ws_message(message)
                            # 至少成功处理1条消息
                            retry_count = 0
                except asyncio.CancelledError:
                    raise
                except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
                    # 掉线重连
                    pass
                finally:
                    self._ws = None
                    if self._game_heartbeat_task is not None:
                        self._game_heartbeat_task.cancel()

                    if self._ws_heartbeat_task is not None:
                        self._ws_heartbeat_task.cancel()

                # 准备重连
                retry_count += 1
                logger.warning('room=%d is reconnecting, retry_count=%d', self.room_id, retry_count)
                await asyncio.sleep(1)
        finally:
            await self._app_end()

    async def _game_heart(self):
        while True:
            await asyncio.sleep(self.game_heartbeat_interval)
            await self._app_heartbeat()

    async def _ws_heart(self):
        while True:
            await asyncio.sleep(self.ws_heartbeat_interval)

    async def _ws_heartbeat(self):
        await self._ws_send(b'', Operation.HEARTBEAT)

    async def _ws_send(self, data: dict | str | bytes, operation: Operation):
        if isinstance(data, dict):
            data = json_.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')
        header = HEADER_STRUCT.pack(*HeaderTuple(
            pack_len=HEADER_STRUCT.size + len(data),
            raw_header_size=HEADER_STRUCT.size,
            ver=1,
            operation=operation,
            seq_id=1
        ))
        await self._ws.send_bytes(header + data)

    async def _on_ws_connect(self):
        """
        websocket连接成功
        """
        await self._send_auth()
        self._heartbeat_timer_task = asyncio.create_task(self._ws_heart())

    async def _send_auth(self):
        await self._ws_send(self._start_data.websocket_info.auth_body, Operation.AUTH)

    async def _app_start(self):
        await self.app.start(self._session, self.room_owner_auth_code)

    async def _app_end(self):
        await self.app.end(self._session)

    async def _app_heartbeat(self):
        await self.app.heartbeat(self._session)
