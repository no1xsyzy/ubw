from typing import Annotated

from pydantic import Field

from ._b_base import BilibiliClientABC
from ._livebase import LiveClientABC, HandlerInterface
from .bilibili import BilibiliUnauthorizedClient, BilibiliCookieClient, BilibiliClient
from .openlive import OpenLiveClient
from .testing import MockClient, MockBilibiliClient
from .wsweb import WSWebCookieLiveClient

LiveClient = Annotated[WSWebCookieLiveClient | OpenLiveClient | MockClient, Field(discriminator='clientc')]

__all__ = (
    'BilibiliClientABC',
    'BilibiliUnauthorizedClient', 'BilibiliCookieClient', 'MockBilibiliClient',
    'BilibiliClient',
    'LiveClientABC', 'HandlerInterface',
    'OpenLiveClient', 'WSWebCookieLiveClient', 'MockClient',
    'LiveClient',
)
