import functools
import os
from typing import *

import aiofiles
import aiohttp
from pydantic import TypeAdapter

from bilibili.models import Response, InfoByRoom, DanmuInfo, RoomEmoticons, FingerSPI, Host, RoomPlayInfo

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
EMOTICON_URL = 'https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons'
FINGER_SPI_URL = 'https://api.bilibili.com/x/frontend/finger/spi'
ROOM_PLAY_INFO_URL = 'https://api.live.bilibili.com/xlive/app-room/v2/index/getRoomPlayInfo'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

F = TypeVar('F')


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


@auto_session
async def get_info_by_room(room_id: int, type_: Type[_Type] = InfoByRoom, *, session: aiohttp.ClientSession) -> _Type:
    async with session.get(ROOM_INIT_URL,
                           params={'room_id': room_id},
                           headers={'User-Agent': USER_AGENT}) as res:
        data = TypeAdapter(Response[type_]).validate_python(await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_danmaku_server(room_id: int, type_: Type[_Type] = DanmuInfo, *, session: aiohttp.ClientSession) -> _Type:
    async with session.get(DANMAKU_SERVER_CONF_URL,
                           params={'id': room_id, 'type': 0},
                           headers={'User-Agent': USER_AGENT}) as res:
        data = TypeAdapter(Response[type_]).validate_python(await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_emoticons(room_id: int, platform: str = 'pc', type_: Type[_Type] = RoomEmoticons, *,
                        session: aiohttp.ClientSession) -> _Type:
    async with session.get(EMOTICON_URL,
                           params={'platform': platform, 'id': room_id},
                           headers={'User-Agent': USER_AGENT}) as res:
        data = TypeAdapter(Response[type_]).validate_python(await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_finger_spi(type_: Type[_Type] = FingerSPI,
                         *, session: aiohttp.ClientSession) -> _Type:
    async with session.get(FINGER_SPI_URL, headers={'User-Agent': USER_AGENT}) as res:
        data = TypeAdapter(Response[type_]).validate_python(await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_room_play_info(room_id: int, quality: int = 10000,
                             type_: Type[_Type] = RoomPlayInfo, *, session: aiohttp.ClientSession) -> _Type:
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
    async with session.get(ROOM_PLAY_INFO_URL, params={
        'build': 6215200,
        'codec': "0,1",
        'device_name': "VTR-AL00",
        'format': "0,1,2,3,4,5,6,7",
        'platform': 'android',
        'protocol': "0,1,2,3,4,5,6,7",
        'qn': quality,
        'room_id': room_id,
    }, cookies=cookies, headers={'user-agent': USER_AGENT}) as res:
        data = TypeAdapter(Response[type_]).validate_python(await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)
