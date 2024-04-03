from functools import cached_property
from typing import TYPE_CHECKING
from unittest.mock import Mock, AsyncMock

from ._base import *


class MockHandler(BaseHandler):
    cls: Literal['mock'] = 'mock'

    start = cached_property(lambda self: Mock(name='start'))
    astart = cached_property(lambda self: AsyncMock(name='astart'))
    handle = cached_property(lambda self: AsyncMock(name='handle'))

    if TYPE_CHECKING:
        start: Mock
        astart: AsyncMock
        handle: AsyncMock
