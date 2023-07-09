from typing import Any

from ._base import *


class CommonNoticeDanmakuSegmentBase(BaseModel):
    type: int
    text: str | None = None

    background_color: Any = None
    background_color_dark: Any = None
    font_bold: Any = None
    font_color: Any = None
    font_color_dark: Any = None
    highlight_font_color: Any = None
    highlight_font_color_dark: Any = None
    img_height: Any = None
    img_width: Any = None
    img_url: Any = None


class CommonNoticeDanmakuSegment1(CommonNoticeDanmakuSegmentBase):
    type: Literal[1]


class CommonNoticeDanmakuSegment2(CommonNoticeDanmakuSegmentBase):
    type: Literal[2]


class CommonNoticeDanmakuSegment3(CommonNoticeDanmakuSegmentBase):
    type: Literal[3]
    uri: str


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


class CommonNoticeDanmakuCommand(CommandModel):
    cmd: Literal['COMMON_NOTICE_DANMAKU']
    data: CommonNoticeDanmakuData
