from contextlib import contextmanager
from contextvars import ContextVar
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
    'Emoji',
    'Record',
)

StreamView = Annotated[Union[SimpleStreamView, LiveStreamView, Richy, Web], Field(discriminator='uic')]

global_stream_view: ContextVar[StreamView | None] = ContextVar('global_stream_view', default=None)


def get_global_stream_view():
    sv = global_stream_view.get()
    if sv is None:
        sv = Richy()
        global_stream_view.set(sv)
    return sv


@contextmanager
def set_global_stream_view(sv):
    tok = global_stream_view.set(sv)
    try:
        yield
    finally:
        global_stream_view.reset(tok)
