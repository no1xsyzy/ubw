from ._base import *


class Item(BaseModel):
    goods_id: str
    goods_name: str
    source: int
    goods_icon: str
    is_pre_sale: int
    activity_info: None
    pre_sale_info: None
    early_bird_info: None
    coupon_discount_price: str
    selected_text: str
    is_gift_buy: int
    goods_price: str
    goods_max_price: str
    reward_info: None
    goods_tag_list: None
    provide_name: str


class Data(BaseModel):
    change_type: int
    title: str
    item: list[Item]


class SelectedGoodsInfoCommand(CommandModel):
    cmd: Literal['SELECTED_GOODS_INFO']
    data: Data
