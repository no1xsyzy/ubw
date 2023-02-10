import functools
from typing import *

import aiohttp
from pydantic import parse_obj_as

from bilibili.models import Response, InfoByRoom

ROOM_INIT_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom'
DANMAKU_SERVER_CONF_URL = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo'


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


@auto_session
async def get_info_by_room(room_id: int, *, session: aiohttp.ClientSession) -> InfoByRoom:
    async with session.get(ROOM_INIT_URL, params={'room_id': room_id}) as res:
        data = parse_obj_as(Response[InfoByRoom], await res.json())
        if data.code == 0:
            return data.data
        else:
            raise BilibiliApiError(data.message)
