from functools import cached_property
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from ._base import *


class MockHandler(BaseHandler):
    cls: Literal['mock'] = 'mock'

    start = cached_property(lambda self: AsyncMock(name='start'))
    handle = cached_property(lambda self: AsyncMock(name='handle'))

    if TYPE_CHECKING:
        start: AsyncMock
        handle: AsyncMock
