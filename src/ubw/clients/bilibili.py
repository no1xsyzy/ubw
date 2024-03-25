import abc
import functools
import http.cookies
import logging
import os
import re
from pathlib import Path
from typing import *

import aiofiles
import aiohttp
from multidict import CIMultiDict
from pydantic import BaseModel, Field
from yarl import URL

from ubw.models.bilibili import *

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
EMOTICON_URL = 'https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons'
FINGER_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'
ROOM_PLAY_INFO_URL = 'https://api.live.bilibili.com/xlive/app-room/v2/index/getRoomPlayInfo'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

F = TypeVar('F')

logger = logging.getLogger('ubw.bilibili')

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


class BilibiliApiError(Exception):
    pass


def auto_session(func: F) -> F:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        session = None
        try:
            if 'session' not in kwargs:
                session = kwargs['session'] = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            result = await func(*args, **kwargs)
            return result
        finally:
            if session is not None:
                await session.close()

    return wrapper


_Type = TypeVar('_Type')


class BilibiliClientABC(BaseModel, abc.ABC):
    auth_type: str
    headers: dict[str, str] = {}
    user_agent: str = USER_AGENT
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

    async def get_info_by_room(self, room_id: int) -> InfoByRoom:
        async with self.session.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                    params={'room_id': room_id}) as res:
            data = Response[InfoByRoom].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_info_by_room_raw(self, room_id: int) -> InfoByRoom:
        async with self.session.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                    params={'room_id': room_id}) as res:
            json_ = await res.json()
            if json_['code'] == 0:
                return json_['data']
            else:
                raise BilibiliApiError(json_['message'])

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

    async def get_dynamic(self, dynamic_id: int, features: list[str] = ()) -> Dynamic:
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
        async with self.session.get("https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space",
                                    params=params) as res:
            data = Response[OffsetList[DynamicItem]].model_validate(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def iter_user_dynamic(self, uid):
        has_more = True
        offset = 0
        while has_more:
            d = await self.get_user_dynamic(uid, offset)
            has_more = d.has_more
            offset = d.offset
            for item in d.items:
                yield item


class BilibiliUnauthorizedClient(BilibiliClientABC):
    auth_type: Literal['no'] = 'no'

    def make_session(self, timeout=None, **kwargs):
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)
        cookie_jar = aiohttp.CookieJar()
        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)
        return aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)


class BilibiliCookieClient(BilibiliClientABC):
    auth_type: Literal['cookie'] = 'cookie'
    cookie_file: Path | None = None

    @functools.cached_property
    def _cookies(self):
        return http.cookies.SimpleCookie()

    async def read_cookie(self, use='default'):
        match use:
            case 'env':
                s = os.environ.get('UBW_COOKIE_FILE')
            case 'config':
                s = self.cookie_file
            case 'default':
                s = os.environ.get('UBW_COOKIE_FILE')
                if s is None:
                    s = self.cookie_file
            case _:
                raise ValueError('`use` must be one of `env`, `config`, `default`')

        if s is None:
            raise ValueError('no cookie file provided, use UBW_COOKIE_FILE or config.toml to specify')

        s = Path(s).resolve()
        logger.debug(f"reading cookies from {s}")

        async with aiofiles.open(s, mode='rt', encoding='utf-8') as f:
            async for line in f:
                line = line.strip()
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                if not line or line.startswith('#'):
                    continue
                domain, subdomains, path, httponly, expires, name, value = line.split('\t')
                subdomains = subdomains == 'TRUE'
                httponly = httponly == 'TRUE'
                from email.utils import formatdate
                expires = formatdate(int(expires), usegmt=True)
                self._cookies[name] = value
                self._cookies[name]['domain'] = domain
                self._cookies[name]['expires'] = expires
                self._cookies[name]['path'] = path
                self._cookies[name]['httponly'] = httponly

    async def __aenter__(self):
        await self.read_cookie()
        return await super().__aenter__()

    def make_session(self, default_cookies=True, timeout=None, **kwargs):
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)

        cookie_jar = aiohttp.CookieJar()
        if default_cookies:
            cookie_jar.update_cookies(self._cookies, URL('https://www.bilibili.com'))

        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)

        return aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)


BilibiliClient = Annotated[BilibiliCookieClient | BilibiliUnauthorizedClient, Field(discriminator='auth_type')]
