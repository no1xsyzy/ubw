from ._base import *


class PriceInfo(BaseModel):
    activity: None
    normal: None


class ShoppingExplainCardData(BaseModel):
    active_info: None
    activity_info: None
    btn_info: None
    coupon_discount_price: float
    coupon_id: str
    coupon_info: None
    coupon_name: str
    early_bird_info: None
    gift_buy_info: None
    goods_icon: str
    goods_id: int
    goods_max_price: str
    goods_name: str
    goods_price: float
    goods_sort_id: int
    goods_tag_list: None
    h5_url: str
    is_exclusive: bool
    is_pre_sale: int
    jump_url: str
    pre_sale_info: None
    price_info: PriceInfo
    reward_info: None
    sale_status: int
    sei_status: int
    selling_point: str
    source: int
    status: int
    timestamp: datetime
    uid: int
    unique_id: int
    virtual_extra_info: None


class ShoppingExplainCardCommand(CommandModel):
    cmd: Literal['SHOPPING_EXPLAIN_CARD']
    data: ShoppingExplainCardData
