from ._base import *


class ReenterLiveRoomData(BaseModel):
    room_id: int
    request_random_sec_range: int
    reason: int  # 1可能代表开启了带密码直播


class ReenterLiveRoomCommand(CommandModel):
    """强制刷新直播间，可能是因为开启了密码"""
    cmd: Literal['REENTER_LIVE_ROOM']
    data: ReenterLiveRoomData
    roomid: int
