from ._base import *


class Data(BaseModel):
    order_id: int
    order_status: int
    roomid: int
    timestamp: datetime
    uid: int


class SpreadOrderStartCommand(CommandModel):
    cmd: Literal['SPREAD_ORDER_START']
    data: Data
