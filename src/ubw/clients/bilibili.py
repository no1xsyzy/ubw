import abc
import functools
import http.cookies
import logging
import os
from pathlib import Path
from typing import *

import aiofiles
import aiohttp
from multidict import CIMultiDict
from pydantic import BaseModel, Field
from yarl import URL

from ubw.models.bilibili import Response, InfoByRoom, DanmuInfo, RoomEmoticons, FingerSPI, RoomPlayInfo

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
EMOTICON_URL = 'https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons'
FINGER_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'
ROOM_PLAY_INFO_URL = 'https://api.live.bilibili.com/xlive/app-room/v2/index/getRoomPlayInfo'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

F = TypeVar('F')

logger = logging.getLogger('ubw.bilibili')


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
