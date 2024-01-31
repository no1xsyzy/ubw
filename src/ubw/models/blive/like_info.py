from ._base import *


class LikeInfoV3UpdateData(BaseModel):
    click_count: int


class LikeInfoV3UpdateCommand(CommandModel):
    cmd: Literal['LIKE_INFO_V3_UPDATE']
    data: LikeInfoV3UpdateData


class ContribInfo(BaseModel):
    grade: int


class FansMedal(BaseModel):
    anchor_roomid: int
    guard_level: int
    icon_id: int
    is_lighted: int
    medal_color: Color
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    medal_name: str
    score: int
    special: str
    target_id: int


class LikeInfoV3ClickData(BaseModel):
    contribution_info: ContribInfo
    dmscore: int
    fans_medal: FansMedal
    identities: list[int]
    like_icon: str
    like_text: str
    msg_type: int
    show_area: int
    uid: int
    uname: str
    uname_color: str


class LikeInfoV3ClickCommand(CommandModel):
    cmd: Literal['LIKE_INFO_V3_CLICK']
    data: LikeInfoV3ClickData


class DanmakuStyle(BaseModel):
    background_color: None


class ContentSegment(BaseModel):
    font_color: Color
    text: str
    type: int


class LikeInfoV3NoticeData(BaseModel):
    content_segments: list[ContentSegment]
    danmaku_style: DanmakuStyle
    terminals: list[int]


class LikeInfoV3NoticeCommand(CommandModel):
    cmd: Literal['LIKE_INFO_V3_NOTICE']
    data: LikeInfoV3NoticeData
