from typing import Annotated, Union

from ._base import *
from .console import ConsoleUI
from .live import LiveUI
from .richy import Richy
from .web import Web

__all__ = (
    'UI',
    'ConsoleUI', 'LiveUI', 'Richy', 'Web',
    'StreamUI',
    'Segment',
    'PlainText', 'Anchor', 'User', 'Room', 'RoomTitle', 'ColorSeeSee', 'DebugInfo', 'Currency', 'Picture',
    'Record',
)

UI = Annotated[Union[ConsoleUI, LiveUI, Richy, Web], Field(discriminator='uic')]
