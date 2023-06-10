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
