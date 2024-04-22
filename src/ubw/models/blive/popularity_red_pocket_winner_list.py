from typing import NamedTuple

from ._base import *


class Award(BaseModel):
    award_big_pic: str
    award_name: str
    award_pic: str
    award_price: int
    award_type: int


class WinnerInfo(NamedTuple):
    uid: int
    uname: str
    entrance: int
    gift_id: int


class NewWinnerInfo(NamedTuple):
    uid: int
    uname: str
    entrance: int
    gift_id: int
    field5: bool


class WinnerField6(BaseModel):
    channel: int
    op_type: int
    payTxt: int
    isGuardWelfare: int


class WinnerInfo8(NamedTuple):
    uid: int
    uname: str
    entrance: int
    gift_id: int
    field5: bool
    field6: WinnerField6 | None
    timestamp: datetime
    ruid: int


class Data(BaseModel):
    awards: dict[str, Award]
    lot_id: int
    total_num: int
    version: int
    winner_info: list[WinnerInfo | NewWinnerInfo | WinnerInfo8]
    rp_type: int = 0
    timestamp: int = 0  # always zero ???
    award_num: int = 0


class PopularityRedPocketWinnerListCommand(CommandModel):
    """红包赢家列表"""
    cmd: Literal['POPULARITY_RED_POCKET_WINNER_LIST']
    data: Data


class PopularityRedPocketV2WinnerListCommand(CommandModel):
    """红包赢家列表V2"""
    cmd: Literal['POPULARITY_RED_POCKET_V2_WINNER_LIST']
    data: Data
