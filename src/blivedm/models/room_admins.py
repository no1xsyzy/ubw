from ._base import *


class RoomAdminsCommand(CommandModel):
    cmd: Literal['ROOM_ADMINS']
    uids: list[int]
