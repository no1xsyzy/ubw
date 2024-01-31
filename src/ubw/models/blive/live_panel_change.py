from ._base import *


class LivePanelChangeData(BaseModel):
    type: int
    scatter: Scatter


class LivePanelChangeCommand(CommandModel):
    cmd: Literal['LIVE_PANEL_CHANGE']
    data: LivePanelChangeData
