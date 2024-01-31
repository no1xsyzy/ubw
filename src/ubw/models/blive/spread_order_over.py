from ._base import *


class Data(BaseModel):
    order_id: int
    order_status: int
    timestamp: datetime
    uid: int


class SpreadOrderOverCommand(CommandModel):
    cmd: Literal['SPREAD_ORDER_OVER']
    data: Data
