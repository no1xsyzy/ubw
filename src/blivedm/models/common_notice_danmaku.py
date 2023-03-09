from ._base import *


class CommonNoticeDanmakuSegment(BaseModel):
    font_color: Color
    font_color_dark: Color
    highlight_font_color: Color | None = None
    highlight_font_color_dark: Color | None = None
    text: str
    type: int


class CommonNoticeDanmakuStyle(BaseModel):
    background_color: Color | None
    background_color_dark: Color | None


class CommonNoticeDanmakuData(BaseModel):
    biz_id: int | None = None
    content_segments: list[CommonNoticeDanmakuSegment]
    danmaku_style: CommonNoticeDanmakuStyle | None = None
    danmaku_uri: str | None = None
    dmscore: int
    terminals: list[int]


class CommonNoticeDanmakuCommand(CommandModel):
    cmd: Literal['COMMON_NOTICE_DANMAKU']
    data: CommonNoticeDanmakuData
