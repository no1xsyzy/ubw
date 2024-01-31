from ._base import *


class SysMsgCommand(CommandModel):
    cmd: Literal['SYS_MSG']
    msg: str
    url: str
