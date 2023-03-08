from ._base import *


class OnlineRankCountData(BaseModel):
    count: int


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData
