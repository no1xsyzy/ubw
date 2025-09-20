from __future__ import annotations

from ._base import *


class Data(BaseModel):
    num: int
    text_small: str
    text_large: str


class Model(BaseModel):
    cmd: str
    data: Data


class CollaborationLiveWatchedCommand(CommandModel):
    cmd: Literal['COLLABORATION_LIVE_WATCHED']
    data: Data
