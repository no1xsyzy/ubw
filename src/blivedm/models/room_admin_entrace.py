from ._base import *


class RoomAdminEntranceCommand(CommandModel):
    cmd: Literal['room_admin_entrance']
    dmscore: int
    level: int
    msg: str
    uid: int
