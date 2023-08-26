from ._base import *


class Data(BaseModel):
    type: int
    uid: int
    uname: str
    uface: str
    gift_id: int
    gift_name: str
    gift_num: int
    price: int
    paid: bool
    msg: str
    fans_medal_level: int
    guard_level: int
    timestamp: datetime
    anchor_lottery: None
    pk_info: None
    anchor_info: None
    combo_info: None


class LiveInteractiveGameCommand(CommandModel):
    cmd: Literal['LIVE_INTERACTIVE_GAME']
    data: Data
