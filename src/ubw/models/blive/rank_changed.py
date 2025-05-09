from ._base import *


class Data(BaseModel):
    uid: int
    rank: int
    countdown: int
    timestamp: datetime
    on_rank_name_by_type: str
    rank_name_by_type: str
    url_by_type: str
    rank_by_type: int
    rank_type: int
    url: str = ''
    sub_rank_type: int = 0


class RankChangedCommand(CommandModel):
    cmd: Literal['RANK_CHANGED', 'RANK_CHANGED_V2']
    data: Data
