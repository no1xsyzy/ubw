from ._base import *


class CommonNoticeDanmakuSegmentBase(BaseModel):
    type: int
    text: str | None = None

    background_color: list[Color] | None = None
    background_color_dark: None = None
    font_bold: None = None
    font_color: Color | None = None
    font_color_dark: Color | None = None
    highlight_font_color: Color | None = None
    highlight_font_color_dark: Color | None = None
    img_height: None = None
    img_width: None = None
    img_url: None = None
    uri: str | None = None


class CommonNoticeDanmakuSegment1(CommonNoticeDanmakuSegmentBase):
    type: Literal[1]


class CommonNoticeDanmakuSegment2(CommonNoticeDanmakuSegmentBase):
    type: Literal[2]


class CommonNoticeDanmakuSegment3(CommonNoticeDanmakuSegmentBase):
    type: Literal[3]


CommonNoticeDanmakuSegment = Annotated[
    CommonNoticeDanmakuSegment1 | CommonNoticeDanmakuSegment2 | CommonNoticeDanmakuSegment3,
    Field(discriminator='type')]


class CommonNoticeDanmakuStyle(BaseModel):
    background_color: Color | list[Color] | None = None
    background_color_dark: Color | list[Color] | None = None


class CommonNoticeDanmakuData(BaseModel):
    biz_id: int | None = None
    content_segments: list[CommonNoticeDanmakuSegment]
    danmaku_style: CommonNoticeDanmakuStyle | None = None
    danmaku_uri: str | None = None
    dmscore: int = 0
    terminals: list[int]
    room_id: int = 0


class CommonNoticeDanmakuCommand(CommandModel):
    cmd: Literal['COMMON_NOTICE_DANMAKU']
    data: CommonNoticeDanmakuData
