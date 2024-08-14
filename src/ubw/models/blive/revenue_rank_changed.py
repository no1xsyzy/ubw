from ._base import *


class Data(BaseModel):
    conf_id: int
    rank_name: str
    uid: int
    rank: int
    icon_url_blue: str
    icon_url_pink: str
    icon_url_grey: str
    action_type: int
    timestamp: datetime
    msg_id: str
    jump_url_link: str


class RevenueRankChangedCommand(CommandModel):
    cmd: Literal['REVENUE_RANK_CHANGED']
    data: Data
