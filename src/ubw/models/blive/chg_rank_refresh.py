from ._base import *


class Data(BaseModel):
    cmd: Literal['CHG_RANK_REFRESH']
    rank_type: int
    rank_module: str
    room_id: int
    ruid: int
    need_refresh: bool
    version: datetime


class ChgRankRefreshCommand(CommandModel):
    cmd: Literal['CHG_RANK_REFRESH']
    data: Data
