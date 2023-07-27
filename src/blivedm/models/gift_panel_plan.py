from ._base import *


class CountMapItem(BaseModel):
    desc: str
    effect_id: int
    horizontal_svga: str
    num: int
    special_color: str
    text: str
    vertical_svga: str
    web_svga: str


class GiftConfig(BaseModel):
    animation_frame_num: int
    bag_gift: int
    bind_roomid: int
    bind_ruid: int
    broadcast: int
    bullet_head: str
    bullet_tail: str
    coin_type: str
    combo_resources_id: int
    corner_background: str
    corner_color_bg: str
    corner_mark: str
    corner_mark_color: str
    count_map: list[CountMapItem]
    desc: str
    diy_count_map: int
    draw: int
    effect: int
    effect_id: int
    first_tips: str
    frame_animation: str
    full_sc_horizontal: str
    full_sc_horizontal_svga: str
    full_sc_vertical: str
    full_sc_vertical_svga: str
    full_sc_web: str
    gif: str
    gift_attrs: list[int]
    gift_banner: None
    gift_type: int
    goods_id: int
    has_imaged_gift: int
    id: int
    img_basic: str
    img_dynamic: str
    left_corner_background: str
    left_corner_text: str
    limit_interval: int
    max_send_limit: int
    name: str
    price: int
    privilege_required: int
    rights: str
    rule: str
    stay_time: int
    type: int
    webp: str
    weight: int


class Gift(BaseModel):
    config: GiftConfig | None
    float_sc_effect: None
    full_sc_effect: None
    gift_id: int
    show: bool
    special_type: int


class Data(BaseModel):
    action: int
    gift_list: list[Gift]
    special_type_sort: list[int] | None


class GiftPanelPlanCommand(CommandModel):
    cmd: Literal['GIFT_PANEL_PLAN']
    data: Data
