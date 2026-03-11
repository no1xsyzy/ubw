from __future__ import annotations

from ._base import *


class SendMaster(BaseModel):
    uname: str
    uid: int


class GiftInfo(BaseModel):
    gift_url: str
    gif: str
    has_imaged_gift: int
    img_basic: str
    webp: str


class Data(BaseModel):
    biz_type: int
    unlock_benefit_url: str
    giftId: int
    giftName: str
    super_batch_gift_num: int
    demarcation: int
    uid: int
    uname: str
    face: str
    num: int
    guard_level: int
    price: int
    discount_price: int
    action: str
    crit_prob: int
    is_special_batch: int
    magnification: int
    combo_stay_time: int
    combo_resources_id: int
    tag_image: str
    timestamp: int
    batch_combo_id: str
    combo_total_coin: int
    total_coin: int
    sender_uinfo: Uinfo
    send_master: SendMaster
    receiver_uinfo: Uinfo
    is_naming: bool
    gift_info: GiftInfo


class GiftComboCommandInfo(BaseModel):
    cmd: str
    data: Data


class GiftComboCommand(GiftComboCommandInfo, CommandModel):
    cmd: Literal['GIFT_COMBO']
