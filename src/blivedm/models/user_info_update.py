from ._base import *


class Data(BaseModel):
    room_id: int
    type: int
    uid: int


class UserInfoUpdateCommand(CommandModel):
    cmd: Literal['USER_INFO_UPDATE']
    data: Data
