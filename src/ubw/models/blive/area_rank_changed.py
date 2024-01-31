from ._base import *


class AreaRankChangedData(BaseModel):
    action_type: int
    conf_id: int
    icon_url_blue: str
    icon_url_grey: str
    icon_url_pink: str
    jump_url_link: str
    jump_url_pc: str
    jump_url_pink: str
    jump_url_web: str
    msg_id: str
    rank: int
    rank_name: str
    timestamp: datetime
    uid: int


class AreaRankChangedCommand(CommandModel):
    cmd: Literal['AREA_RANK_CHANGED']
    data: AreaRankChangedData
