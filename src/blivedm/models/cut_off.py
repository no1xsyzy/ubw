from ._base import *


class CutOffCommand(CommandModel):
    cmd: Literal['CUT_OFF']
    msg: str
    roomid: int
