from ._base import *


class OnlineRankTop3Info(BaseModel):
    msg: str
    rank: int
    is_mystery: bool = False
    uid: int | None = None


class OnlineRankTop3Data(BaseModel):
    dmscore: int
    list: list[OnlineRankTop3Info]


class OnlineRankTop3Command(CommandModel):
    cmd: Literal['ONLINE_RANK_TOP3']
    data: OnlineRankTop3Data
