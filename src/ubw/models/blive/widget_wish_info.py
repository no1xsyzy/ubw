from ._base import *


class WishItem(BaseModel):
    gift_id: int
    target_num: int
    gift_img: str
    gift_price: int
    gift_name: str
    wish_status: int


class WishStatusInfoItem(BaseModel):
    wish_status_msg: str
    wish_status_img: str
    wish_status: int


class Data(BaseModel):
    sid: int
    wish: list[WishItem]
    jump_url: str
    wish_status: int
    card_text: str | None = None
    modal_text: str
    button_text: str | None = None
    show_time: int
    ts: datetime
    tid: int
    wish_status_info: list[WishStatusInfoItem]


class WidgetWishInfoCommand(CommandModel):
    cmd: Literal['WIDGET_WISH_INFO']
    data: Data
