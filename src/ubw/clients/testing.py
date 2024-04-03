from functools import cached_property
from unittest.mock import Mock, AsyncMock

from ._b_base import BilibiliClientABC
from ._livebase import *


class MockBilibiliClient(BilibiliClientABC):
    auth_type: Literal['mock_bilibili_client'] = 'mock_bilibili_client'

    read_cookie = cached_property(lambda self: AsyncMock(name='read_cookie'))
    make_session = cached_property(lambda self: Mock(name='make_session'))
    close = cached_property(lambda self: AsyncMock(name='close'))
    __aenter__ = cached_property(lambda self: AsyncMock(name='__aenter__'))

    get_account_info = cached_property(lambda self: AsyncMock(name='get_account_info'))
    get_user_dynamic = cached_property(lambda self: AsyncMock(name='get_user_dynamic'))
    get_info_by_room = cached_property(lambda self: AsyncMock(name='get_info_by_room'))
    get_danmaku_server = cached_property(lambda self: AsyncMock(name='get_danmaku_server'))


class MockClient(LiveClientABC):
    clientc: Literal['mock'] = 'mock'

    bilibili_client: MockBilibiliClient | None = None

    close = cached_property(lambda self: AsyncMock(name='close'))
    join = cached_property(lambda self: AsyncMock(name='join'))
    start = cached_property(lambda self: Mock(name='start'))
    stop = cached_property(lambda self: Mock(name='stop'))
    user_ident = cached_property(lambda self: Mock(name='user_ident'))
    add_handler = cached_property(lambda self: Mock(name='add_handler'))


class MockWebsocket:
    def __init__(self, side_effect=None):
        try:
            side_effect = iter(side_effect)

            async def sd():
                next_side_effect = next(side_effect)
                if isinstance(next_side_effect, Exception):
                    raise next_side_effect
                else:
                    return next_side_effect

            self.side_effect = sd
        except TypeError:
            if callable(side_effect):
                self.side_effect = side_effect
            else:
                async def sd():
                    if isinstance(side_effect, Exception):
                        raise side_effect
                    else:
                        return side_effect

                self.side_effect = sd

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    close = cached_property(lambda self: AsyncMock(name='close'))

    closed = False

    send_bytes = cached_property(lambda self: AsyncMock(name='send_bytes'))

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.side_effect()
