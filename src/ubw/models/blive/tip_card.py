from __future__ import annotations

from ._base import *


class Extra(BaseModel):
    isCloseItemSize: bool
    itemCode: int


class Data(BaseModel):
    biz_id: int
    extra: Json[Extra]


class TipCardCommand(CommandModel):
    cmd: Literal['TIP_CARD']
    data: Data
