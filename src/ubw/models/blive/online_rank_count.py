from ._base import *


class OnlineRankCountData(BaseModel):
    online_count: int | None = None
    count: int | None = None


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData
