from ._base import *


class Data(BaseModel):
    timestamp: datetime
    message: str


class LiveRoomToastMessageCommand(CommandModel):
    cmd: Literal['LIVE_ROOM_TOAST_MESSAGE']
    data: Data
    timestamp: datetime
