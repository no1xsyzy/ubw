import abc
import functools
import http.cookies
import logging
import os
import urllib.parse
from pathlib import Path
from typing import *

import aiofiles
import aiohttp
from multidict import CIMultiDict
from pydantic import BaseModel, Field, TypeAdapter
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

    @property
    @abc.abstractmethod
    def session(self):
        ...

    async def close(self):
        await self.session.close()

    async def get_info_by_room(self, room_id: int) -> InfoByRoom:
        async with self.session.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom',
                                    params={'room_id': room_id}) as res:
            data = TypeAdapter(Response[InfoByRoom]).validate_python(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_danmaku_server(self, room_id: int) -> DanmuInfo:
        async with self.session.get(DANMAKU_SERVER_CONF_URL,
                                    params={'id': room_id, 'type': 0}) as res:
            data = TypeAdapter(Response[DanmuInfo]).validate_python(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_emoticons(self, room_id: int, platform: str = 'pc') -> RoomEmoticons:
        async with self.session.get(EMOTICON_URL,
                                    params={'platform': platform, 'id': room_id}) as res:
            data = TypeAdapter(Response[RoomEmoticons]).validate_python(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_finger_spi(self, ) -> FingerSPI:
        async with self.session.get(FINGER_SPI_URL, headers={'User-Agent': USER_AGENT}) as res:
            data = TypeAdapter(Response[FingerSPI]).validate_python(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)

    async def get_room_play_info(self, room_id: int, quality: int = 10000) -> RoomPlayInfo:
        cookies = {}
        if (s := os.environ.get('UBW_COOKIE_FILE')) is not None:
            async with aiofiles.open(s, mode='rt', encoding='utf-8') as f:
                async for line in f:
                    line = line.strip()
                    if line.startswith('#HttpOnly_'):
                        line = line[len('#HttpOnly_'):]
                    if not line or line.startswith('#'):
                        continue
                    domain, subdomains, path, httponly, expires, name, value = line.split('\t')
                    cookies[name] = value
        async with self.session.get(ROOM_PLAY_INFO_URL, params={
            'build': 6215200,
            'codec': "0,1",
            'device_name': "VTR-AL00",
            'format': "0,1,2,3,4,5,6,7",
            'platform': 'android',
            'protocol': "0,1,2,3,4,5,6,7",
            'qn': quality,
            'room_id': room_id,
        }, cookies=cookies, headers={'user-agent': USER_AGENT}) as res:
            data = TypeAdapter(Response[RoomPlayInfo]).validate_python(await res.json())
            if data.code == 0:
                return data.data
            else:
                raise BilibiliApiError(data.message)


class BilibiliCookieClient(BilibiliClientABC):
    auth_type: Literal['cookie'] = 'cookie'
    cookie_file: Path | None = None

    @functools.cached_property
    def session(self):
        return self.make_session()

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
                value = urllib.parse.unquote(value)
                self._cookies[name] = value
                self._cookies[name]['domain'] = domain
                self._cookies[name]['expires'] = expires
                self._cookies[name]['path'] = path
                self._cookies[name]['httponly'] = httponly

    def make_session(self, default_cookies=True, headers=None, cookie_jar=None, **kwargs):
        if headers:
            headers = CIMultiDict(headers)
        else:
            headers = CIMultiDict()

        headers.setdefault('User-Agent', USER_AGENT)

        if not cookie_jar:
            cookie_jar = aiohttp.CookieJar()
        if default_cookies:
            cookie_jar.update_cookies(self._cookies, URL('https://www.bilibili.com'))

        return aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, **kwargs)


BilibiliClient = Annotated[BilibiliCookieClient, Field(discriminator='auth_type')]
