from ._base import *


class WealthNotifyInfo(BaseModel):
    effect_key: int
    has_items_changed: int
    level: str
    send_time: datetime
    status: int


class WealthNotifyData(BaseModel):
    flag: int
    info: WealthNotifyInfo


class WealthNotifyCommand(CommandModel):
    """荣耀等级提示，具体不明"""
    cmd: Literal['WEALTH_NOTIFY']
    data: WealthNotifyData
