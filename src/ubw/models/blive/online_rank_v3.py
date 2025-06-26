from ._base import *


class Data(BaseModel):
    pb: str


class OnlineRankV3Command(CommandModel):
    cmd: Literal['ONLINE_RANK_V3']
    data: Data
