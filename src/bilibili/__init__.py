import functools
from typing import *

import aiohttp
from pydantic import parse_obj_as

from bilibili.models import Response, InfoByRoom, DanmuInfo, RoomEmoticons

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'
EMOTICON_URL = 'https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons'

RETURN_VAR = TypeVar('RETURN_VAR')


class BilibiliApiError(Exception):
    pass


def auto_session(func: Callable[[...], RETURN_VAR]):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> RETURN_VAR:
        session = None
        if 'session' not in kwargs:
            session = kwargs['session'] = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        result = await func(*args, **kwargs)
        if session is not None:
            await session.close()
        return result

    return wrapper


_Type = TypeVar('_Type')


@auto_session
async def get_info_by_room(room_id: int, type_: Type[_Type] = InfoByRoom, *, session: aiohttp.ClientSession) -> _Type:
    async with session.get(ROOM_INIT_URL, params={'room_id': room_id}) as res:
        data = parse_obj_as(Response[type_], await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_danmaku_server(room_id: int, type_: Type[_Type] = DanmuInfo, *, session: aiohttp.ClientSession) -> _Type:
    async with session.get(DANMAKU_SERVER_CONF_URL, params={'id': room_id}) as res:
        data = parse_obj_as(Response[type_], await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)


@auto_session
async def get_emoticons(room_id: int, platform: str = 'pc', type_: Type[_Type] = RoomEmoticons, *,
                        session: aiohttp.ClientSession) -> _Type:
    async with session.get(EMOTICON_URL, params={'platform': platform, 'id': room_id}) as res:
        data = parse_obj_as(Response[type_], await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)
