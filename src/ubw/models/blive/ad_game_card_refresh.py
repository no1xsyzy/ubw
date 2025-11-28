from __future__ import annotations

from ._base import *


class Data(BaseModel):
    room_id: str
    card_id: str
    game_card_click_uv: str


class AdGameCardRefreshCommand(CommandModel):
    cmd: Literal['AD_GAME_CARD_REFRESH']
    data: Data
