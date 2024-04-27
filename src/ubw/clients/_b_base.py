import abc
import logging
import re
from contextvars import ContextVar
from typing import Literal, TypeVar

import aiohttp
from pydantic import BaseModel

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
    _mixin_key: str | None = None

    @abc.abstractmethod
    def make_session(self):
        ...

    @property
    def session(self):
        if self._session is None:
            self._session = self.make_session()
        return self._session

    @session.setter
    def session(self, v):
        self._session = v

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
            async with self.session.get(url, **kwargs) as res:
                data = Response[data_model].model_validate((await res.json()))
                if data.code == 0:
                    logger.debug(f"successfully get {url!r} {kwargs!r}")
                    return data.data
                else:
                    raise BilibiliApiError(data.message)
        except Exception as e:
            if (try_count := _try_count.get()) < self.try_limit:
                _try_count.set(try_count + 1)
                return await self._get_model(data_model, url, **kwargs)
            logger.exception(f"Bilibili API Error on get {url!r} {kwargs!r}", exc_info=e)
            raise

    async def _get_raw(self, url, **kwargs) -> dict:
        try:
            async with self.session.get(url, **kwargs) as res:
                data = await res.json()
                if data['code'] == 0:
                    logger.debug(f"successfully get {url!r} {kwargs!r}")
                    return data['data']
                else:
                    raise BilibiliApiError(data['message'])
        except Exception as e:
            if (try_count := _try_count.get()) < self.try_limit:
                _try_count.set(try_count + 1)
                return await self._get_raw(url, **kwargs)
            logger.exception(f"Bilibili API Error on get {url!r} {kwargs!r}", exc_info=e)
            raise

    async def get_info_by_room(self, room_id: int) -> InfoByRoom:
        return await self._get_model(InfoByRoom,
                                     'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                     params={'room_id': room_id})

    async def get_info_by_room_raw(self, room_id: int):
        return await self._get_raw('https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                   params={'room_id': room_id})

    async def get_danmaku_server(self, room_id: int) -> DanmuInfo:
        async with self.session.get(DANMAKU_SERVER_CONF_URL,
                                    params={'id': room_id, 'type': 0}) as res:
            data = Response[DanmuInfo].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_emoticons(self, room_id: int, platform: str = 'pc') -> RoomEmoticons:
        async with self.session.get(EMOTICON_URL,
                                    params={'platform': platform, 'id': room_id}) as res:
            data = Response[RoomEmoticons].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_finger_spi(self, ) -> FingerSPI:
        async with self.session.get(FINGER_SPI_URL) as res:
            data = Response[FingerSPI].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_room_play_info(self, room_id: int, quality: int = 10000) -> RoomPlayInfo:
        async with self.session.get(ROOM_PLAY_INFO_URL, params={
            'build': 6215200,
            'codec': "0,1",
            'device_name': "VTR-AL00",
            'format': "0,1,2,3,4,5,6,7",
            'platform': 'android',
            'protocol': "0,1,2,3,4,5,6,7",
            'qn': quality,
            'room_id': room_id,
        }) as res:
            data = Response[RoomPlayInfo].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_dynamic(self, dynamic_id: int | str, features: list[str] = ()) -> Dynamic:
        async with self.session.get('https://api.bilibili.com/x/polymer/web-dynamic/v1/detail',
                                    params={'id': dynamic_id, 'features': ','.join(features)}, ) as res:
            data = Response[Dynamic].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                request_info = res.request_info
                raise BilibiliApiError(data.message)

    async def get_account_info(self, uid: int) -> AccountInfo:
        async with self.session.get('https://api.bilibili.com/x/space/wbi/acc/info',
                                    params=await self.enclose_wbi({'mid': uid})) as res:
            data = Response[AccountInfo].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def enclose_wbi(self, params):
        import time
        from urllib.parse import urlencode
        import hashlib

        if self._mixin_key is None:
            data = await self.get_nav()
            j = RE_FN.match(data.wbi_img_url).group(1) + RE_FN.match(data.wbi_img_sub_url).group(1)
            s = ""
            for i in MAGIC:
                if i < len(j):
                    s += j[i]
            mixin_key = self._mixin_key = s[:32]
        else:
            mixin_key = self._mixin_key

        params.pop("w_rid", None)
        params["wts"] = int(time.time())
        params["web_location"] = 1550101
        ek = urlencode(sorted(params.items())) + mixin_key
        params["w_rid"] = hashlib.md5(ek.encode(encoding="utf-8")).hexdigest()
        return params

    async def get_nav(self) -> Nav:
        async with self.session.get("https://api.bilibili.com/x/web-interface/nav") as res:
            data = Response[Nav].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_user_dynamic(self, uid, offset=0) -> OffsetList[DynamicItem]:
        params = {'host_mid': uid, 'features': 'itemOpusStyle'}
        if offset != 0:
            params['offset'] = offset

        return await self._get_model(
            OffsetList[DynamicItem],
            "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space", params=params)

    async def iter_user_dynamic(self, uid):
        has_more = True
        offset = 0
        while has_more:
            d = await self.get_user_dynamic(uid, offset)
            has_more = d.has_more
            offset = d.offset
            for item in d.items:
                yield item

    async def get_video_pagelist(self, bvid):
        return await self._get_model(list[VideoP], 'https://api.bilibili.com/x/player/pagelist',
                                     params={'bvid': bvid})

    async def get_video_download(self, bvid, cid):
        return await self._get_model(VideoPlayInfo, 'https://api.bilibili.com/x/player/playurl',
                                     params={'bvid': bvid, 'cid': cid, 'qn': 127, 'otype': 'json', 'fnval': 4048},
                                     headers={'referer': 'https://www.bilibili.com/video/' + bvid})

    async def get_video_download_raw(self, bvid, cid):
        return await self._get_raw('https://api.bilibili.com/x/player/playurl',
                                   params={'bvid': bvid, 'cid': cid, 'qn': 127, 'otype': 'json', 'fnval': 4048},
                                   headers={'referer': 'https://www.bilibili.com/video/' + bvid})
