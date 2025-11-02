from __future__ import annotations

from ._base import *


class Datum(BaseModel):
    room_id: int
    match_status: int
    home_team_name: str
    away_team_name: str
    home_team_icon: str
    away_team_icon: str
    home_team_score: int
    away_team_score: int
    time_stamp: int


class LiveMultiViewEventChangeCommand(CommandModel):
    cmd: Literal['LIVE_MULTI_VIEW_EVENT_CHANGE']
    data: list[Datum]
