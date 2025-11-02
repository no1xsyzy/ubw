from __future__ import annotations

from ._base import *


class Pop(BaseModel):
    app_url: str
    biz_data: str
    v_auto_pop: bool
    h_auto_pop: bool


class IconInfoV2(BaseModel):
    biz_id: int
    bubble_last_time: int  # seconds
    bubble_url: str


class PlayerDanmaku(BaseModel):
    content: str
    app_url: str
    click_enable: bool


class Data(BaseModel):
    biz_name: str
    token_id: str
    scatter_seconds: int
    pop: Pop
    icon_info_v2: IconInfoV2
    player_danmaku: PlayerDanmaku


class Model(BaseModel):
    cmd: str
    data: Data


class CommonBigEventCommand(CommandModel):
    cmd: Literal['COMMON_BIG_EVENT']
    data: Data
