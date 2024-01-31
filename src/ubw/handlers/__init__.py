from typing import Annotated

from pydantic import Field

from ._base import BaseHandler
from .bhashm import HashMarkHandler
from .danmakup import DanmakuPHandler
from .dump_raw import DumpRawHandler
from .saver import SaverHandler
from .strange_stalker import StrangeStalkerHandler
from .wocpian import PianHandler

Handler = Annotated[
    HashMarkHandler | DanmakuPHandler | DumpRawHandler | SaverHandler | StrangeStalkerHandler | PianHandler,
    Field(discriminator='cls')]
