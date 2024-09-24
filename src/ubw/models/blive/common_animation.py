from ._base import *


class Data(BaseModel):
    uid: int
    effect_id: int
    demarcation: int
    order_id: str


class CommonAnimationCommand(CommandModel):
    cmd: Literal['COMMON_ANIMATION']
    data: Data
