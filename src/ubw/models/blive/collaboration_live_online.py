from __future__ import annotations

from ._base import *


class Data(BaseModel):
    num: int
    text: str


class Model(BaseModel):
    cmd: str
    data: Data


class CollaborationLiveOnlineCommand(CommandModel):
    cmd: Literal['COLLABORATION_LIVE_ONLINE']
    data: Data
