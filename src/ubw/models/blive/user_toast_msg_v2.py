from ._base import *


class GuardInfo(BaseModel):
    guard_level: int
    role_name: str
    room_guard_count: int
    op_type: int
    start_time: datetime
    end_time: datetime


class PayInfo(BaseModel):
    payflow_id: str
    price: int
    num: int
    unit: str


class GiftInfo(BaseModel):
    gift_id: int


class EffectInfo(BaseModel):
    effect_id: int
    room_effect_id: int
    face_effect_id: int
    room_gift_effect_id: int
    room_group_effect_id: int


class Option(BaseModel):
    anchor_show: bool
    user_show: bool
    is_group: int
    is_show: int
    source: int
    svga_block: int
    color: Color


class Data(BaseModel):
    sender_uinfo: Uinfo
    receiver_uinfo: Uinfo
    guard_info: GuardInfo
    group_guard_info: None
    pay_info: PayInfo
    gift_info: GiftInfo
    effect_info: EffectInfo
    option: Option
    toast_msg: str


class UserToastMsgV2Command(CommandModel):
    cmd: Literal['USER_TOAST_MSG_V2']
    data: Data
