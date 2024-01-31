from ._base import *


class WatchedChangeData(BaseModel):
    num: int
    text_small: str
    text_large: str


class WatchedChangeCommand(CommandModel):
    cmd: Literal['WATCHED_CHANGE']
    data: WatchedChangeData
