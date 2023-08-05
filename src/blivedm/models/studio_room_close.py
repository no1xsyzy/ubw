from ._base import *


class StudioRoomCloseCommand(CommandModel):
    cmd: Literal['STUDIO_ROOM_CLOSE']
    msg: str
    roomid: int
