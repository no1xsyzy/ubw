from ._base import *


class Data(BaseModel):
    name: str
    room_id: int
    ruid: int
    time: datetime
    uid: int


class RankRemCommand(CommandModel):
    cmd: Literal['RANK_REM']
    data: Data
