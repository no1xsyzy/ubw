from ._base import *


class StopLiveRoomListData(BaseModel):
    room_id_list: list[int]


class StopLiveRoomListCommand(CommandModel):
    cmd: Literal['STOP_LIVE_ROOM_LIST']
    data: StopLiveRoomListData
