from ._base import *


class ComboData(BaseModel):
    id: int
    status: int
    content: str
    cnt: int
    guide: str
    left_duration: int
    fade_duration: int
    prefix_icon: str = ''


class DataData(BaseModel):
    combo: list[ComboData]
    merge_interval: int
    card_appear_interval: int
    send_interval: int


class Data(BaseModel):
    id: int
    status: int
    type: int
    data: DataData
    dmscore: int = 0

    validate_extra = field_validator('data', mode='before')(strange_dict)


class DmInteractionCommand(CommandModel):
    cmd: Literal['DM_INTERACTION']
    data: Data
