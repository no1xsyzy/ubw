from ._base import *


class Data(BaseModel):
    room_id: int
    status: int
    url: str


class BenefitStatusCommand(CommandModel):
    cmd: Literal['BENEFIT_STATUS']
    data: Data
