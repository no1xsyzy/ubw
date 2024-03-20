from ._base import *


class OnlineRankV2Info(BaseModel):
    face: str
    guard_level: int
    is_mystery: bool = False
    uinfo: Uinfo
    rank: int
    score: int = 0
    uid: int
    uname: str


class OnlineRankV2Data(BaseModel):
    rank_type: str
    online_list: list[OnlineRankV2Info] = Field(validation_alias=AliasChoices('online_list', 'list'))


class OnlineRankV2Command(CommandModel):
    cmd: Literal['ONLINE_RANK_V2']
    data: OnlineRankV2Data
