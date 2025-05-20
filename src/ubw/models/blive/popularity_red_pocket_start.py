from ._base import *


class Award(BaseModel):
    gift_id: int
    gift_name: str
    gift_pic: str
    num: int


class RpGuardInfo(BaseModel):
    rp_guard_icon: str
    rp_guard_text_icon: str
    rp_guard_flag_icon: str
    discount_rent: float  # maybe percentage


class PopularityRedPocketStartData(BaseModel):
    awards: list[Award]
    current_time: datetime
    danmu: str
    end_time: datetime
    h5_url: str
    join_requirement: int
    last_time: int
    lot_config_id: int
    lot_id: int
    lot_status: int
    remove_time: datetime
    replace_time: datetime
    sender_face: str
    sender_name: str
    sender_uid: int
    start_time: datetime
    total_price: int
    user_status: int
    wait_num: int
    wait_num_v2: int = 0
    is_mystery: bool = False
    rp_type: int = 0
    sender_uinfo: Uinfo | None = None
    icon_url: str = ''
    animation_icon_url: str = ''
    rp_guard_info: RpGuardInfo | None = None
    anchor_h5_url: str = ''


class PopularityRedPocketStartCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_START']
    data: PopularityRedPocketStartData


class PopularityRedPocketV2StartCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_V2_START']
    data: PopularityRedPocketStartData
