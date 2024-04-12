from ._base import *


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
