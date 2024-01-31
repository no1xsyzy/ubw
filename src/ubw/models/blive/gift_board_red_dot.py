from ._base import *


class Data(BaseModel):
    categoryL1: str


class GiftBoardRedDotCommand(CommandModel):
    cmd: Literal['GIFT_BOARD_RED_DOT']
    data: Data
