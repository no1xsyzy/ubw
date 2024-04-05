from ._base import *


class OfficialInfo(BaseModel):
    role: int
    title: str
    desc: str
    type: int


class OfficialBaseInfo(BaseModel):
    uid: int
    title: str
    uname: str
    face: str
    gender: str
    official_info: OfficialInfo


class Data(BaseModel):
    event_type: int
    room_id: int
    official_room_id: int
    official_anchor_id: int
    countdown: int
    scatter_time: int
    sub_title: str
    desc: str = ''
    official_base_info: OfficialBaseInfo
    current_room_status: int | None = None


class OfficialRoomEventCommand(CommandModel):
    cmd: Literal['OFFICIAL_ROOM_EVENT']
    data: Data
