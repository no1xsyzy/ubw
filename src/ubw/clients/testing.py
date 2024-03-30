from functools import cached_property
from unittest.mock import Mock, AsyncMock

from ._b_base import BilibiliClientABC
from ._livebase import *


class MockClient(LiveClientABC):
    clientc: Literal['mock'] = 'mock'

    close = cached_property(lambda self: AsyncMock(name='close'))
    join = cached_property(lambda self: AsyncMock(name='join'))
    start = cached_property(lambda self: Mock(name='start'))
    stop = cached_property(lambda self: Mock(name='stop'))
    user_ident = cached_property(lambda self: Mock(name='user_ident'))
    add_handler = cached_property(lambda self: Mock(name='add_handler'))


class MockBilibiliClient(BilibiliClientABC):
    auth_type: Literal['mock_bilibili_client'] = 'mock_bilibili_client'

    make_session = cached_property(lambda self: Mock(name='session'))
