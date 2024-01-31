from ._base import *


class LiveMultiViewChangeData(BaseModel):
    scatter: Scatter


class LiveMultiViewChangeCommand(CommandModel):
    cmd: Literal['LIVE_MULTI_VIEW_CHANGE']
    data: LiveMultiViewChangeData
