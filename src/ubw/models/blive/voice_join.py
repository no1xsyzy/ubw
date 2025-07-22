from ._base import *
from .. import CommandModel


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
    notify_count: int = 0
    red_point: int = 0


class VoiceJoinRoomCountInfoCommand(CommandModel):
    cmd: Literal['VOICE_JOIN_ROOM_COUNT_INFO']
    data: VoiceJoinRoomCountInfoData
    room_id: int


class VoiceJoinSwitch(BaseModel):
    room_id: int
    room_status: int
    root_status: int
    conn_type: int
    anchor_uid: int


class VoiceJoinSwitchCommand(CommandModel):
    cmd: Literal['VOICE_JOIN_SWITCH', 'VOICE_JOIN_SWITCH_V2']
    data: VoiceJoinSwitch
    room_id: int
