from ._base import *


class OnlineRankTop3Info(BaseModel):
    msg: str
    rank: int


class OnlineRankTop3Data(BaseModel):
    dmscore: int
    list: list[OnlineRankTop3Info]


class OnlineRankTop3Command(CommandModel):
    cmd: Literal['ONLINE_RANK_TOP3']
    data: OnlineRankTop3Data
