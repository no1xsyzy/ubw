from ._base import *


class Data(BaseModel):
    room_id: int
    ruid: int
    type: str
    need_refresh_tab: bool


class PopularityRankTabChgCommand(CommandModel):
    cmd: Literal['POPULARITY_RANK_TAB_CHG']
    data: Data
