from ._base import *


class HotBuyNumData(BaseModel):
    goods_id: int
    num: int


class HotBuyNumCommand(CommandModel):
    cmd: Literal['HOT_BUY_NUM']
    data: HotBuyNumData
