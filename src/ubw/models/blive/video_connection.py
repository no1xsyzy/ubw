from ._base import *


class VideoConnectionJoinStartData(BaseModel):
    status: int
    invited_uid: int
    channel_id: int
    invited_uname: str
    invited_face: str
    start_at: datetime
    current_time: datetime


class VideoConnectionJoinStartCommand(CommandModel):
    cmd: Literal['VIDEO_CONNECTION_JOIN_START']
    data: VideoConnectionJoinStartData
    roomid: int


class VideoConnectionJoinEndData(BaseModel):
    channel_id: int
    start_at: datetime
    toast: str
    current_time: datetime


class VideoConnectionJoinEndCommand(CommandModel):
    cmd: Literal['VIDEO_CONNECTION_JOIN_END']
    data: VideoConnectionJoinEndData
    roomid: int


class VideoConnectionMsgData(BaseModel):
    channel_id: int
    current_time: datetime
    dmscore: int
    toast: str


class VideoConnectionMsgCommand(CommandModel):
    cmd: Literal['VIDEO_CONNECTION_MSG']
    data: VideoConnectionMsgData
