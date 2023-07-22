from ._base import *


class Award(BaseModel):
    gift_id: int
    gift_name: str
    gift_pic: str
    num: int


class PopularityRedPocketStartData(BaseModel):
    awards: list[Award]
    current_time: datetime
    danmu: str
    end_time: datetime
    h5_url: str
    join_requirement: int
    last_time: int
    lot_config_id: int
    lot_id: int
    lot_status: int
    remove_time: datetime
    replace_time: datetime
    sender_face: str
    sender_name: str
    sender_uid: int
    start_time: datetime
    total_price: int
    user_status: int
    wait_num: int


class PopularityRedPocketStartCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_START']
    data: PopularityRedPocketStartData
