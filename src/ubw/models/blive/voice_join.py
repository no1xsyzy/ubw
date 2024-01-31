from ._base import *


class VoiceJoinStatusData(BaseModel):
    room_id: int
    status: int
    channel: str
    channel_type: str
    uid: int
    user_name: str
    head_pic: str
    guard: int
    start_at: datetime
    current_time: datetime
    web_share_link: str


class VoiceJoinStatusCommand(CommandModel):
    cmd: Literal['VOICE_JOIN_STATUS']
    data: VoiceJoinStatusData
    room_id: int


class VoiceJoinListData(BaseModel):
    cmd: str
    room_id: int
    category: int
    apply_count: int
    red_point: int
    refresh: int


class VoiceJoinListCommand(CommandModel):
    cmd: Literal['VOICE_JOIN_LIST']
    data: VoiceJoinListData
    room_id: int


class VoiceJoinRoomCountInfoData(BaseModel):
    cmd: str
    room_id: int
    root_status: int
    room_status: int
    apply_count: int


class VoiceJoinRoomCountInfoCommand(CommandModel):
    cmd: Literal['VOICE_JOIN_ROOM_COUNT_INFO']
    data: VoiceJoinRoomCountInfoData
    room_id: int
