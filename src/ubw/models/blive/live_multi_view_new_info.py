from ._base import *


class Room(BaseModel):
    order_id: int
    room_id: int
    room_name: str
    live_status: int
    jump_url: str


class MatchInfo(BaseModel):
    match_status: int
    home_team_name: str
    away_team_name: str
    home_team_icon: str
    away_team_icon: str
    home_team_score: int
    away_team_score: int


class RelationView(BaseModel):
    order_id: int
    view_type: int
    view_id: int
    view_name: str
    title: str
    cover: str
    jump_url: str
    switch: bool
    num: int
    watch_icon: str
    live_status: int
    text_small: str
    use_view_vt: bool
    anchor_face: str
    match_live_room: bool
    match_info: MatchInfo | None
    duration: int
    up_name: str
    pub_date: str
    gather_id: int
    sub_name: str = ""


class GatherRoom(BaseModel):
    order_id: int
    gather_title: str
    exposure_mode: int
    icon: str
    gather_id: int
    gather_type: int


class Data(BaseModel):
    title: str
    room_id: int
    copy_writing: str
    bg_image: str
    sub_slt_color: Color | Literal['']
    sub_bg_color: Color | Literal['']
    sub_text_color: Color | Literal['']
    view_type: int
    room_list: list[Room] | None
    relation_view: list[RelationView] | None
    view_pattern: int
    gather_room_list: list[GatherRoom] | None


class LiveMultiViewNewInfo(CommandModel):
    cmd: Literal['LIVE_MULTI_VIEW_NEW_INFO']
    data: Data
