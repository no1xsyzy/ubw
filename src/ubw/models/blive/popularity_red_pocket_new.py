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
    wait_num_v2: int = 0
    group_medal: GroupMedal | None = None
    is_mystery: bool = False
    sender_info: Uinfo | None = None
    gift_icon: str = ''
    rp_type: int = 0


class PopularityRedPocketNewCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_NEW']
    data: PopularityRedPocketNewData


class PopularityRedPocketV2NewCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_V2_NEW']
    data: PopularityRedPocketNewData
