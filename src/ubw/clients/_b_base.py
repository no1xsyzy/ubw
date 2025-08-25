import abc
import asyncio
import hashlib
import logging
import re
import time
from contextvars import ContextVar
from datetime import timedelta
from typing import Literal, TypeVar
from urllib.parse import urlencode, quote

import aiohttp
import pydantic
import sentry_sdk
from bilibili_api import user, Credential
from pydantic import BaseModel, TypeAdapter

from ubw.models.bilibili import *

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
EMOTICON_URL = 'https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons'
FINGER_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'
ROOM_PLAY_INFO_URL = 'https://api.live.bilibili.com/xlive/app-room/v2/index/getRoomPlayInfo'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

# magics for wbi sign
RE_FN = re.compile(r'.+/(\w+)\..+')
MAGIC = [
    46, 47, 18, 2, 53, 8, 23, 32,
    15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19,
    29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61,
    26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63,
    57, 62, 11, 36, 20, 34, 44, 52,
]

__all__ = ('BilibiliApiError', 'BilibiliClientABC', 'Literal', 'USER_AGENT',)

logger = logging.getLogger('ubw.clients._b_base')
_try_count = ContextVar('try_count', default=1)
_T = TypeVar('_T')


class BilibiliApiError(Exception):
    pass


class BilibiliClientABC(BaseModel, abc.ABC):
    auth_type: str
    headers: dict[str, str] = {}

    user_agent: str = USER_AGENT
    try_limit: int = 3

    _session: aiohttp.ClientSession | None = None
    _credential: Credential | None = None
    _mixin_key: str | None = None

    @abc.abstractmethod
    async def make_session(self) -> aiohttp.ClientSession:
        ...

    @abc.abstractmethod
    async def make_credential(self) -> Credential:
        pass

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = await self.make_session()
        return self._session

    async def get_credential(self) -> Credential:
        if self._credential is None:
            self._credential = await self.make_credential()
        return self._credential

    async def close(self):
        if self._session is not None:
            await self._session.close()
        self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get_model(self, data_model: type[_T], url, **kwargs) -> _T:
        try:
            async with (await self.get_session()).get(url, **kwargs) as res:
                j = await res.json()
                try:  # process ValidationError here to tell linter that j is created
                    data = Response[data_model].model_validate(j)
                except pydantic.ValidationError as e:
                    sentry_sdk.capture_event(
                        event={'level': 'warning', 'message': f'error parsing model {data_model.__name__}'},
                        contexts={'ValidationError': {'data': j, 'error': e.errors(include_url=False)}},
                        tags={'model': data_model.__name__, 'type': 'get-model-parsing'},
                    )
                    raise
                if data.code == 0:
                    logger.debug(f"successfully get {url!r} {kwargs!r}")
                    return data.data
                else:
                    raise BilibiliApiError(data.message)
        except Exception as e:  # TODO: only capture retry-able exceptions
            if isinstance(e, pydantic.ValidationError):  # this cannot be solved by retry
                raise
            if isinstance(e, BilibiliApiError):  # this cannot be solved by retry
                if e.args == ("房间已加密",):
                    raise
            if (try_count := _try_count.get()) < self.try_limit:
                tok = _try_count.set(try_count + 1)
                try:
                    logger.warning(f"get {url!r} {kwargs!r} (try {try_count + 1}/{self.try_limit})")
                    return await self._get_model(data_model, url, **kwargs)
                finally:
                    _try_count.reset(tok)
            logger.exception(f"Bilibili API Error on get {url!r} {kwargs!r}", exc_info=e)
            raise

    async def _get_raw(self, url, **kwargs) -> dict:
        try:
            async with (await self.get_session()).get(url, **kwargs) as res:
                data = await res.json()
                if data['code'] == 0:
                    logger.debug(f"successfully get {url!r} {kwargs!r}")
                    return data['data']
                else:
                    raise BilibiliApiError(data['message'])
        except Exception as e:  # TODO: only capture retry-able exceptions
            if (try_count := _try_count.get()) < self.try_limit:
                _try_count.set(try_count + 1)
                return await self._get_raw(url, **kwargs)
            logger.exception(f"Bilibili API Error on get {url!r} {kwargs!r}", exc_info=e)
            raise

    async def get_info_by_room(self, room_id: int) -> InfoByRoom:
        credential = await self.get_credential()
        from bilibili_api import live
        r = live.LiveRoom(room_display_id=room_id, credential=credential)
        return InfoByRoom.model_validate(await r.get_room_info())

    async def get_info_by_room_raw(self, room_id: int):
        credential = await self.get_credential()
        from bilibili_api import live
        r = live.LiveRoom(room_display_id=room_id, credential=credential)
        return await r.get_room_info()

    async def get_danmaku_server(self, room_id: int) -> DanmuInfo:
        credential = await self.get_credential()
        from bilibili_api import live
        r = live.LiveRoom(room_display_id=room_id, credential=credential)
        return DanmuInfo.model_validate(await r.get_danmu_info())

    async def get_emoticons(self, room_id: int, platform: str = 'pc') -> RoomEmoticons:
        async with (await self.get_session()).get(EMOTICON_URL,
                                                  params={'platform': platform, 'id': room_id}) as res:
            data = Response[RoomEmoticons].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_finger_spi(self, ) -> FingerSPI:
        async with (await self.get_session()).get(FINGER_SPI_URL) as res:
            data = Response[FingerSPI].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_room_play_info(self, room_id: int, quality: int = 10000) -> RoomPlayInfo:
        async with (await self.get_session()).get(ROOM_PLAY_INFO_URL, params={
            'build': 6215200,
            'device_name': "VTR-AL00",
            'platform': 'android',

            'protocol': "0,1",
            'format': "0,1,2",
            'codec': "0,1,2",

            'qn': quality,
            'room_id': room_id,

            "no_playurl": "0",
            "mask": "1",
            "dolby": "5",
            "panorama": "1",
            "hdr_type": "0,1",
        }) as res:
            data = Response[RoomPlayInfo].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_dynamic(self, dynamic_id: int | str, features: list[str] = ()) -> Dynamic:
        async with (await self.get_session()).get('https://api.bilibili.com/x/polymer/web-dynamic/v1/detail',
                                                  params={'id': dynamic_id, 'features': ','.join(features)}, ) as res:
            data = Response[Dynamic].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                request_info = res.request_info
                raise BilibiliApiError(data.message)

    async def get_account_info(self, uid: int, ) -> AccountInfo:
        credential = await self.get_credential()
        u = user.User(uid=uid, credential=credential)
        return AccountInfo.model_validate(await u.get_user_info())

    async def enclose_wbi(self, params):
        if self._mixin_key is None:
            nav = await self.get_nav()
            j = RE_FN.match(nav.wbi_img_url).group(1) + RE_FN.match(nav.wbi_img_sub_url).group(1)
            s = ''.join(j[i] for i in MAGIC if i < len(j))
            mixin_key = self._mixin_key = s[:32]
        else:
            mixin_key = self._mixin_key

        params.pop("w_rid", None)
        params["wts"] = int(time.time())
        params.setdefault("web_location", 1550101)
        ek = urlencode(sorted(params.items()), quote_via=quote) + mixin_key
        params["w_rid"] = hashlib.md5(ek.encode(encoding="utf-8")).hexdigest()
        return params

    async def get_nav(self) -> Nav:
        async with (await self.get_session()).get("https://api.bilibili.com/x/web-interface/nav") as res:
            data = Response[Nav].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_user_dynamic(self, uid, offset="") -> OffsetList[DynamicItem]:
        credential = await self.get_credential()
        u = user.User(uid=uid, credential=credential)
        return TypeAdapter(OffsetList[DynamicItem]).validate_python(await u.get_dynamics_new(offset=offset))

    async def iter_user_dynamic(self, uid):
        has_more = True
        offset = ""
        while has_more:
            d = await self.get_user_dynamic(uid, offset)
            has_more = d.has_more
            offset = d.offset
            for item in d.items:
                yield item

    async def two_way_iter_user_dynamic(self, uid, *, poll_interval: timedelta = timedelta(seconds=60)):
        f"""
        :param uid: 想要获取动态的UID
        :param poll_interval: （必须使用关键词）抓取未来方向动态的时间间隔，接受 timedelta 格式。
        :return: 一对 async iterator (past, future)，可分别使用 async for 获取信息。对于past，将从当前往回搜索，需自行注意循环速度。
        future 则持续 yield 动态，需注意潜在的阻塞。
        """
        d = await self.get_user_dynamic(uid)

        async def past(dd):
            has_more = dd.has_more
            offset = dd.offset
            while has_more:
                for item in dd.items:
                    yield item
                dd = await self.get_user_dynamic(uid, offset)
                has_more = dd.has_more
                offset = dd.offset

        async def future(dd):
            while True:
                future_p = max(it.pub_date for it in dd.items) if dd.items else None
                jj = []
                fetch_more = True
                offset = ""
                while fetch_more:
                    dd = await self.get_user_dynamic(uid, offset=offset)
                    extends = dd.items if future_p is None else [it for it in dd.items if it.pub_date > future_p]
                    jj.extend(extends)
                    if len(extends) < len(dd.items):
                        fetch_more = False
                    else:
                        offset = dd.offset
                for item in sorted(jj, key=lambda it: it.pub_date):
                    yield item
                await asyncio.sleep(poll_interval.total_seconds())

        return past(d), future(d)

    async def get_video_pagelist(self, bvid):
        from bilibili_api import video
        credential = await self.get_credential()
        v = video.Video(bvid=bvid, credential=credential)
        return TypeAdapter(list[VideoP]).validate_python(await v.get_pages())

    async def get_video_download(self, bvid, cid):
        from bilibili_api import video
        credential = await self.get_credential()
        v = video.Video(bvid=bvid, credential=credential)
        return VideoPlayInfo.model_validate(await v.get_download_url(cid=cid))

    async def get_video_download_raw(self, bvid, cid):
        from bilibili_api import video
        credential = await self.get_credential()
        v = video.Video(bvid=bvid, credential=credential)
        return await v.get_download_url(cid=cid)

    async def get_history_danmaku(self, room_id):
        async with (await self.get_session()).get(
                f"https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid={room_id}&room_type=0") as res:
            data = Response[dict].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def iter_live_danmaku(self, room_id, history=False, connect=True):
        if history:
            for danmaku in (await self.get_history_danmaku(room_id))['room']:
                yield {'cmd': 'X_HISTORY_DANMU', 'info': danmaku}
        if connect:
            from ubw.clients import WSWebCookieLiveClient
            q = asyncio.Queue()

            class PseudoHandler:
                async def handle(self, c, m):
                    await q.put(m)

            live_client = WSWebCookieLiveClient(bilibili_client=self, bilibili_client_owner=False, room_id=room_id)
            live_client.add_handler(PseudoHandler())
            await live_client.start()
            try:
                while True:
                    yield await q.get()
            finally:
                await live_client.stop_and_close()
