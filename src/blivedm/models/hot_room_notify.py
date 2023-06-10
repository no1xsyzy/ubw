from ._base import *


class RandomDelayReq(BaseModel):
    delay: int
    path: str


class HotRoomNotifyData(BaseModel):
    exit_no_refresh: int
    random_delay_req_v2: list[RandomDelayReq]
    threshold: int
    ttl: int


class HotRoomNotifyCommand(CommandModel):
    cmd: Literal['HOT_ROOM_NOTIFY']
    data: HotRoomNotifyData
