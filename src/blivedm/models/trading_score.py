from ._base import *


class TradingScoreData(BaseModel):
    bubble_show_time: timedelta
    num: int
    score_id: int
    uid: int
    update_time: datetime
    update_type: int


class TradingScoreCommand(CommandModel):
    cmd: Literal['TRADING_SCORE']
    data: TradingScoreData
