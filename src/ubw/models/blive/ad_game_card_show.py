from __future__ import annotations

from ._base import *


class Data(BaseModel):
    card_id: str
    status: int
    timestamp: str


class AdGameCardShowCommand(CommandModel):
    cmd: Literal['AD_GAME_CARD_SHOW']
    data: Data
