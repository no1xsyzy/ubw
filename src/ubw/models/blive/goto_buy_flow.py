from ._base import *


class GotoBuyFlowData(BaseModel):
    text: str


class GotoBuyFlowCommand(CommandModel):
    cmd: Literal['GOTO_BUY_FLOW']
    data: GotoBuyFlowData
