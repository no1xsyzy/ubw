from ._base import *


class ChangeRoomInfoCommand(CommandModel):
    cmd: Literal['CHANGE_ROOM_INFO']
    roomid: int
    background: str
