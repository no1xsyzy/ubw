from ._base import *


class CommonNoticeDanmakuSegment(BaseModel):
    font_color: Color
    font_color_dark: Color
    text: str
    type: int


class CommonNoticeDanmakuStyle(BaseModel):
    background_color: Color | None
    background_color_dark: Color | None


class CommonNoticeDanmakuData(BaseModel):
    biz_id: int
    content_segments: list[CommonNoticeDanmakuSegment]
    danmaku_style: CommonNoticeDanmakuStyle
    danmaku_uri: str
    dmscore: int
    terminals: list[int]


class CommonNoticeDanmakuCommand(CommandModel):
    cmd: Literal['COMMON_NOTICE_DANMAKU']
    data: CommonNoticeDanmakuData
