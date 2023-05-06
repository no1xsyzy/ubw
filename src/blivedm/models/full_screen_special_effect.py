from ._base import *


class FullScreenSpecialEffectData(BaseModel):
    ids: list[int]
    platform_in: list[int]
    queue: int
    type: int


class FullScreenSpecialEffectCommand(CommandModel):
    cmd: Literal['FULL_SCREEN_SPECIAL_EFFECT']
    data: FullScreenSpecialEffectData
