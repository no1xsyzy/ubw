from functools import cached_property
from typing import TYPE_CHECKING
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

    if TYPE_CHECKING:
        read_cookie: AsyncMock
        make_session: Mock
        close: AsyncMock
        __aenter__: AsyncMock
        get_account_info: AsyncMock
        get_user_dynamic: AsyncMock
        get_info_by_room: AsyncMock
        get_danmaku_server: AsyncMock


class MockClient(LiveClientABC):
    clientc: Literal['mock'] = 'mock'

    bilibili_client: MockBilibiliClient | None = None

    close = cached_property(lambda self: AsyncMock(name='close'))
    join = cached_property(lambda self: AsyncMock(name='join'))
    start = cached_property(lambda self: Mock(name='start'))
    stop = cached_property(lambda self: Mock(name='stop'))
    user_ident = cached_property(lambda self: Mock(name='user_ident'))
    add_handler = cached_property(lambda self: Mock(name='add_handler'))

    if TYPE_CHECKING:
        close: AsyncMock
        join: AsyncMock
        start: Mock
        stop: Mock
        user_ident: Mock
        add_handler: Mock


class MockWebsocket:
    def __init__(self, side_effect=None):
        self.side_effect = side_effect

    @property
    def side_effect(self):
        return self._side_effect

    @side_effect.setter
    def side_effect(self, value):
        if callable(value):
            self._side_effect = value
        else:
            try:
                value = iter(value)

                async def sd():
                    next_side_effect = next(value)
                    if isinstance(next_side_effect, BaseException):
                        raise next_side_effect
                    else:
                        return next_side_effect

                self._side_effect = sd
            except TypeError:
                async def sd():
                    if isinstance(value, BaseException):
                        raise value
                    else:
                        return value

                self._side_effect = sd

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

    if TYPE_CHECKING:
        close: AsyncMock
        send_bytes: AsyncMock
