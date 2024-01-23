from ._base import *


class OnlineRankCountData(BaseModel):
    online_count: int = Field(validation_alias=AliasChoices('online_count', 'count'))


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData
