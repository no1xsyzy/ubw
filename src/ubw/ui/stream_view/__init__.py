from typing import Annotated, Union

from ._base import *
from .console import SimpleStreamView
from .live import LiveStreamView
from .richy import Richy
from .web import Web

__all__ = (
    'StreamView',
    'SimpleStreamView', 'LiveStreamView', 'Richy', 'Web',
    'BaseStreamView',
    'Segment',
    'PlainText', 'Anchor', 'User', 'Room', 'RoomTitle', 'ColorSeeSee', 'DebugInfo', 'Currency', 'Picture', 'LineBreak',
    'Record',
)

StreamView = Annotated[Union[SimpleStreamView, LiveStreamView, Richy, Web], Field(discriminator='uic')]
