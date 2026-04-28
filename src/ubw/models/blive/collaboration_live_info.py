from __future__ import annotations

from ._base import *


class RelationViewItem(BaseModel):
    order_id: int
    view_type: int
    view_id: int
    view_name: str
    jump_url: str
    live_status: int

    cover: str = ""
    anchor_face: str = ""


class MultiView(BaseModel):
    room_id: int
    copy_writing: str
    bg_image: str
    sub_slt_color: Color | Literal['']
    sub_bg_color: Color | Literal['']
    sub_text_color: Color | Literal['']
    view_type: int
    relation_view: list[RelationViewItem] | None = None
    view_pattern: int

    expand_guide_text: str = "\u5207\u6362\u623f\u95f4\uff0c\u652f\u6301\u76f8\u5e94\u4e3b\u64ad"
    expand_guide_icon: str = "https://i0.hdslb.com/bfs/live/022a16a5116fd3ab8709d22c3bed482185a9c1d7.png"
    activity_name: str = ""


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
