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


class WinnerInfo8(NamedTuple):
    uid: int
    uname: str
    entrance: int
    gift_id: int
    field5: bool
    field6: None
    timestamp: datetime
    ruid: int


class Data(BaseModel):
    awards: dict[str, Award]
    lot_id: int
    total_num: int
    version: int
    winner_info: list[WinnerInfo | NewWinnerInfo | WinnerInfo8]
    rp_type: int = 0
    timestamp: int = 0  # ???
    award_num: int = 0


class PopularityRedPocketWinnerListCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_WINNER_LIST']
    data: Data


class PopularityRedPocketV2WinnerListCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_V2_WINNER_LIST']
    data: Data
