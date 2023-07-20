from ._base import *


class OnlineRankV2Info(BaseModel):
    face: str
    guard_level: int
    rank: int
    uid: int
    uname: str


class OnlineRankV2Data(BaseModel):
    rank_type: str
    list: list[OnlineRankV2Info]


class OnlineRankV2Command(CommandModel):
    cmd: Literal['ONLINE_RANK_V2']
    data: OnlineRankV2Data
