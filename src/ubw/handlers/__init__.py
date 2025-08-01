from typing import Annotated, Union

from pydantic import Field

from ._base import BaseHandler
from .bhashm import HashMarkHandler
from .danmakup import DanmakuPHandler
from .dump_raw import DumpRawHandler
from .edge_collect import EdgeCollector
from .living_status import LivingStatusHandler
from .saver import SaverHandler
from .strange_stalker import StrangeStalkerHandler
from .testing import MockHandler
from .vod import VodHandler
from .vodt import VodTextualHandler
from .warn_nebd import WarnNoEntranceButDanmakuHandler
from .wocpian import PianHandler

Handler = Annotated[
    Union[
        HashMarkHandler,
        DanmakuPHandler,
        DumpRawHandler,
        EdgeCollector,
        SaverHandler,
        StrangeStalkerHandler,
        PianHandler,
        LivingStatusHandler,
        VodHandler,
        VodTextualHandler,
        WarnNoEntranceButDanmakuHandler,
        MockHandler,
    ],
    Field(discriminator='cls')]
