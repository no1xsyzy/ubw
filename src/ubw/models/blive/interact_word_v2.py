from ._base import *


class Data(BaseModel):
    dmscore: int
    pb: str


class InteractWordV2Command(CommandModel):
    cmd: Literal['INTERACT_WORD_V2']
    data: Data
