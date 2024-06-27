from ._base import *


class InteractMode(BaseModel):
    apply_timeout: int
    interact_mode_type: int
    invite_timeout: int
    join_types: list[int]
    position_mode: int


class Cell(BaseModel):
    can_zoom: int
    default_open: int
    height: int
    mobile_avatar_size: int
    mobile_font_size: int
    pc_web_avatar_size: int
    pc_web_font_size: int
    position: int
    width: int
    x: int
    y: int
    z_index: int


class RtcResolution(BaseModel):
    code_rate_init: int
    code_rate_max: int
    code_rate_min: int
    horizontal_height: int
    horizontal_width: int
    vertical_height: int
    vertical_width: int


class LayoutData(BaseModel):
    best_area_show_pos: int
    cells: list[Cell]
    default_cell: Cell
    height: int
    rtc_resolution: RtcResolution
    width: int


class InteractTemplate(BaseModel):
    is_variable_layout: bool
    layout_data: LayoutData
    layout_id: str
    layout_list: None
    show_interact_ui: bool
    template_id: str


class Member(BaseModel):
    face: str
    gender: int
    join_time: datetime
    link_id: str
    position: int
    room_id: int
    uid: int
    uname: str


class Score(BaseModel):
    price: int
    price_text: str
    uid: int


class MultiConnInfo(BaseModel):
    room_owner: int
    scores: list[Score]


class Info(BaseModel):
    biz_session_id: str
    business_label: str
    interact_channel_id: str
    interact_connect_type: int
    interact_max_users: int
    interact_mode: InteractMode
    interact_template: InteractTemplate
    invoking_time: int
    members: list[Member]
    members_version: int
    multi_conn_info: MultiConnInfo
    room_owner: int
    room_start_at: str
    room_start_at_ts: int
    room_status: int
    session_start_at: str
    session_start_at_ts: int
    session_status: int
    system_time_unix: datetime
    trace_id: str
    version: int


class Data(BaseModel):
    anchor_uid: int
    info: Info
    room_id: int


class UniversalEventGiftCommand(CommandModel):
    cmd: Literal['UNIVERSAL_EVENT_GIFT']
    data: Data
