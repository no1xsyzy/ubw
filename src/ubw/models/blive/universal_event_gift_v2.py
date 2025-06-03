from ._base import *


class InteractTemplate(BaseModel):
    template_id: str
    show_interact_ui: bool
    layout_id: str


class MultiConn(BaseModel):
    price: int
    price_text: str


class BizExtraData(BaseModel):
    multi_conn: MultiConn


class Member(BaseModel):
    uid: int
    uname: str
    face: str
    position: int
    join_time: datetime
    link_id: str
    gender: int
    room_id: int
    fans_num: int
    display_name: str
    biz_extra_data: BizExtraData


class MultiConn1(BaseModel):
    show_score: int
    support_full_zoom: int


class BizExtraData1(BaseModel):
    multi_conn: MultiConn1


class Data(BaseModel):
    biz_session_id: str
    interact_channel_id: str
    interact_template: InteractTemplate
    members: list[Member]
    stream_control: None
    version: int
    session_status: int
    business_label: str
    invoking_time: int
    members_version: int
    room_status: int
    system_time_unix: datetime
    room_owner: int
    session_start_at: datetime
    session_start_at_ts: int
    room_start_at: datetime
    room_start_at_ts: int


class UniversalEventGiftV2Command(CommandModel):
    cmd: Literal['UNIVERSAL_EVENT_GIFT_V2']
    data: Data
