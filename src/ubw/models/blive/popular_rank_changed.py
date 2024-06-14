from ._base import *


class PopularRankChangedData(BaseModel):
    cache_key: str
    countdown: int
    rank: int
    timestamp: datetime
    uid: int
    on_rank_name_by_type: str
    rank_name_by_type: str
    url_by_type: str
    rank_by_type: str
    default_url: str


class PopularRankChangedCommand(CommandModel):
    cmd: Literal['POPULAR_RANK_CHANGED']
    data: PopularRankChangedData
