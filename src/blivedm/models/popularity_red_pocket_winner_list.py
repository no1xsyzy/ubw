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


class Data(BaseModel):
    awards: dict[str, Award]
    lot_id: int
    total_num: int
    version: int
    winner_info: list[WinnerInfo | NewWinnerInfo]


class PopularityRedPocketWinnerListCommand(CommandModel):
    cmd: Literal['POPULARITY_RED_POCKET_WINNER_LIST']
    data: Data
