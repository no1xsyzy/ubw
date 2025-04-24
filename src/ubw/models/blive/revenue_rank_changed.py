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
    jump_url_pc: str
    jump_url_pink: str
    jump_url_web: str
    charm_chat_new_name: str = ""
    charm_chat_new_icon: str = ""


class RevenueRankChangedCommand(CommandModel):
    cmd: Literal['REVENUE_RANK_CHANGED']
    data: Data
