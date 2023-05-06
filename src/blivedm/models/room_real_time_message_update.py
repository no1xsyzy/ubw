from ._base import *


class RoomRealTimeMessageUpdateData(BaseModel):
    fans: int
    fans_club: int
    red_notice: int
    roomid: int


class RoomRealTimeMessageUpdateCommand(CommandModel):
    cmd: Literal['ROOM_REAL_TIME_MESSAGE_UPDATE']
    data: RoomRealTimeMessageUpdateData
