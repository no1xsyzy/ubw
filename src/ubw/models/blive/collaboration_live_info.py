from __future__ import annotations

from ._base import *


class RelationViewItem(BaseModel):
    order_id: int
    view_type: int
    view_id: int
    view_name: str
    jump_url: str
    live_status: int


class MultiView(BaseModel):
    room_id: int
    copy_writing: str
    bg_image: str
    sub_slt_color: Color
    sub_bg_color: Color
    sub_text_color: Color
    view_type: int
    relation_view: list[RelationViewItem]
    view_pattern: int


class Data(BaseModel):
    if_collaboration_room: int
    team_id: int
    multi_view: MultiView
    show_multi_view: int


class Model(BaseModel):
    cmd: str
    data: Data


class CollaborationLiveInfoCommand(CommandModel):
    cmd: Literal['COLLABORATION_LIVE_INFO']
    data: Data
