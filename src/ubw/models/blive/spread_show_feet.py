from ._base import *


class Data(BaseModel):
    click: int
    coin_cost: int
    coin_num: int
    order_id: int
    plan_percent: int
    show: int
    timestamp: datetime
    title: str
    total_online: int
    uid: int


class SpreadShowFeetCommand(CommandModel):
    cmd: Literal['SPREAD_SHOW_FEET']
    data: Data
