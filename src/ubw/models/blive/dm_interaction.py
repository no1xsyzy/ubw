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


class DataData2(BaseModel):
    card_appear_interval: int
    reset_cnt: int = -1
    display_flag: int = 0
    cnt: int
    fade_duration: int
    suffix_text: str = '人正在点赞'


class Data(BaseModel):
    id: int
    status: int
    type: int
    data: DataData | DataData2
    dmscore: int = 0

    validate_extra = field_validator('data', mode='before')(strange_dict)


class DmInteractionCommand(CommandModel):
    cmd: Literal['DM_INTERACTION']
    data: Data
