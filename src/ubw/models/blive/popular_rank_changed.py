from ._base import *


class PopularRankChangedData(BaseModel):
    cache_key: str
    countdown: int
    rank: int
    timestamp: datetime
    uid: int


class PopularRankChangedCommand(CommandModel):
    cmd: Literal['POPULAR_RANK_CHANGED']
    data: PopularRankChangedData
