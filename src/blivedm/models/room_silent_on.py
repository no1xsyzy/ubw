from ._base import *


class RoomSilentOnData(BaseModel):
    level: int
    second: int
    type: str


class RoomSilentOnCommand(CommandModel):
    cmd: Literal['ROOM_SILENT_ON']
    data: RoomSilentOnData
