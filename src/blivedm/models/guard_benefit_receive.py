from ._base import *


class Data(BaseModel):
    room_id: int
    url: str


class GuardBenefitReceiveCommand(CommandModel):
    cmd: Literal['GUARD_BENEFIT_RECEIVE']
    data: Data
