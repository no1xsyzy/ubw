from ._base import *


class Data(BaseModel):
    ruid: int
    type: int
    uid: int


class ConfirmAutoFollowCommand(CommandModel):
    cmd: Literal['CONFIRM_AUTO_FOLLOW']
    data: Data
