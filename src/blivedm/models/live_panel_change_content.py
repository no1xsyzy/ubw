from ._base import *


class CustomItem(BaseModel):
    icon: str
    jump_url: str
    note: str
    status: int
    sub_icon: str
    title: str


class Tab(BaseModel):
    aggregation: int
    biz_type: str
    global_id: str
    id: int
    show_guide_bubble: str
    show_outer_aggregation: int
    sub_icon: str
    sub_title: str
    tab_comment: dict[str, str] | None
    tab_topic: dict[str, str] | None
    type: str


class Item(BaseModel):
    biz_id: int
    custom: list[CustomItem] | None
    dynamic_icon: str
    icon: str
    icon_info: None
    jump_url: str
    match_entrance: int
    note: str
    notification: None
    panel_icon: str
    status_type: int
    sub_icon: str
    tab: Tab | None
    title: str
    type_id: int
    weight: float


class Data(BaseModel):
    interaction_list: list[Item]
    is_fixed: int
    is_match: int
    match_bg_image: str
    match_cristina: str
    match_icon: str
    outer_list: list[Item]
    panel_data: None
    setting_list: list[Item]


class LivePanelChangeContentCommand(CommandModel):
    cmd: Literal['LIVE_PANEL_CHANGE_CONTENT']
    data: Data
