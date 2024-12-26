from ._base import *


class RoomSilentData(BaseModel):
    level: int
    second: int
    type: str
    msg: str = ''


class RoomSilentOnCommand(CommandModel):
    cmd: Literal['ROOM_SILENT_ON']
    data: RoomSilentData


class RoomSilentOffCommand(CommandModel):
    cmd: Literal['ROOM_SILENT_OFF']
    data: RoomSilentData
