from ._base import *


class Datum(BaseModel):
    start_time: datetime
    end_time: datetime
    stream: str
    type: int
    ban_ec: bool


class OtherSliceLoadingResultData(BaseModel):
    data: list[Datum]
    live_key: str


class OtherSliceLoadingResultCommand(CommandModel):
    cmd: Literal['OTHER_SLICE_LOADING_RESULT']
    data: OtherSliceLoadingResultData
