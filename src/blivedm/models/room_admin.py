from ._base import *


class RoomAdminsCommand(CommandModel):
    cmd: Literal['ROOM_ADMINS']
    uids: list[int]


class RoomAdminEntranceCommand(CommandModel):
    cmd: Literal['room_admin_entrance']
    dmscore: int
    level: int
    msg: str
    uid: int


class RoomAdminRevokeCommand(CommandModel):
    cmd: Literal['ROOM_ADMIN_REVOKE']
    msg: str
    uid: int
