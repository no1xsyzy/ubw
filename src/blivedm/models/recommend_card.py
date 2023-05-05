from ._base import *


class VirtualExtraInfo(BaseModel):
    goods_type: int
    web_container_type: int


class PriceInf(BaseModel):
    prefix_price: str
    sale_price: str
    suffix_price: str
    strock_price: str
    sale_start_time: datetime
    sale_end_time: datetime
    strock_show: int


class PriceInfo(BaseModel):
    normal: PriceInf | None
    activity: PriceInf | None


class BtnInfo(BaseModel):
    card_btn_status: int
    card_btn_title: str
    card_btn_style: int
    card_btn_jumpurl: str


class ShoppingCardDetail(BaseModel):
    goods_id: str
    goods_name: str
    goods_price: str
    goods_max_price: str
    sale_status: int
    coupon_name: str
    goods_icon: str
    goods_status: str
    source: int
    h5_url: str
    jump_link: str
    schema_url: str
    is_pre_sale: int
    activity_info: None
    pre_sale_info: None
    early_bird_info: None
    timestamp: datetime
    coupon_discount_price: str
    selling_point: str
    hot_buy_num: int
    gift_buy_info: None
    is_exclusive: bool
    coupon_id: str
    reward_info: None
    goods_tag_list: None
    virtual_extra_info: VirtualExtraInfo
    price_info: PriceInfo
    btn_info: BtnInfo
    goods_sort_id: int
    coupon_info: None
    active_info: None
    jump_url: str


class RecommendData(BaseModel):
    shopping_card_detail: ShoppingCardDetail
    recommend_card_extra: None


class RecommendCardData(BaseModel):
    title_icon: str
    recommend_list: list[RecommendData]
    timestamp: datetime


class RecommendCardCommand(CommandModel):
    cmd: Literal['RECOMMEND_CARD']
    data: RecommendCardData
