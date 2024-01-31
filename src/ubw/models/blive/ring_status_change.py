from ._base import *


class RingStatusChangeData(BaseModel):
    status: int


class RingStatusChangeCommand(CommandModel):
    cmd: Literal['RING_STATUS_CHANGE']
    data: RingStatusChangeData


class RingStatusChangeCommandV2(CommandModel):
    cmd: Literal['RING_STATUS_CHANGE_V2']
    data: RingStatusChangeData
