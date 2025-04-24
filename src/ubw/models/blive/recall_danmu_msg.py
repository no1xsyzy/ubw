from ._base import *


class Data(BaseModel):
    recall_type: int
    target_id: int


class RecallDanmuMsgCommand(CommandModel):
    cmd: Literal['RECALL_DANMU_MSG']
    data: Data
