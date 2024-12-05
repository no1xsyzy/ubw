from ._base import *


class LotteryCard(BaseModel):
    button_text: str
    icon: str
    title: str
    show_time: int


class Data(BaseModel):
    notice_type: int
    lottery_card: LotteryCard


class AnchorLotNoticeCommand(CommandModel):
    cmd: Literal['ANCHOR_LOT_NOTICE']
    data: Data
