from ._base import *


class MedalInfo(BaseModel):
    anchor_roomid: int
    anchor_uname: str
    guard_level: int
    icon_id: int
    is_lighted: int
    medal_color: int
    medal_color_border: int
    medal_color_end: int
    medal_color_start: int
    medal_level: int
    medal_name: str
    special: str
    target_id: int


class PopularityRedPocketNewData(BaseModel):
    action: str
    current_time: datetime
    gift_id: int
    gift_name: str
    lot_id: int
    medal_info: MedalInfo
    name_color: str
    num: int
    price: int
    start_time: datetime
    uid: int
    uname: str
    wait_num: int
    wealth_level: int


class PopularityRedPocketNewCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_NEW']
    data: PopularityRedPocketNewData
