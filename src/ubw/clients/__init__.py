from typing import Annotated

from pydantic import Field

from ._livebase import LiveClientABC, HandlerInterface
from .bilibili import BilibiliCookieClient, BilibiliUnauthorizedClient, BilibiliClientABC, BilibiliClient
from .openlive import OpenLiveClient
from .wsweb import WSWebCookieLiveClient

LiveClient = Annotated[WSWebCookieLiveClient | OpenLiveClient, Field(discriminator='clientc')]

__all__ = (
    'BilibiliCookieClient', 'BilibiliUnauthorizedClient', 'BilibiliClientABC', 'BilibiliClient',
    'LiveClientABC', 'HandlerInterface',
    'OpenLiveClient', 'WSWebCookieLiveClient',
    'LiveClient',
)
