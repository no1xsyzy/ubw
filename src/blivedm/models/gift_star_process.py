from ._base import *


class GiftStarProcessData(BaseModel):
    status: int
    tip: str


class GiftStarProcessCommand(CommandModel):
    cmd: Literal['GIFT_STAR_PROCESS']
    data: GiftStarProcessData
