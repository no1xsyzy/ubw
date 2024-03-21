from ._base import *


class Wish(BaseModel):
    type: int
    gift_id: int
    gift_name: str
    gift_img: str
    gift_price: int
    target_num: int
    current_num: int
    wish_name: str
    check_status: int
    check_reason: str
    wish_sub_id: str
    id: str


class WishStatusInfo(BaseModel):
    wish_status_msg: str
    wish_status_img: str
    wish_status: int


class Data(BaseModel):
    wish: list[Wish]
    wish_status: int
    sid: int
    wish_status_info: list[WishStatusInfo]
    wish_name: str
    jump_schema: str = ''
    type: int = 0
    ts: datetime


class WidgetWishListCommand(CommandModel):
    cmd: Literal['WIDGET_WISH_LIST']

    data: Data
