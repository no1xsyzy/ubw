from ._base import *


class SpecialGiftDatum(BaseModel):
    action: str
    content: str
    hadJoin: int
    id: str
    num: int
    storm_gif: str
    time: int  # 看上去像是秒数


class SpecialGiftCommand(CommandModel):
    cmd: Literal['SPECIAL_GIFT']
    data: dict[str, SpecialGiftDatum]
