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


class Data102Data(BaseModel):
    combo: list[ComboData]
    merge_interval: int
    card_appear_interval: int
    send_interval: int
    reset_cnt: int = -1
    display_flag: int = 0


class Data103Data(BaseModel):
    fade_duration: int = 10000
    cnt: int
    card_appear_interval: int = 0
    suffix_text: str = '人关注了主播'
    reset_cnt: int = 0
    display_flag: int = 1


class Data104Data(BaseModel):
    fade_duration: int = 10000
    cnt: int
    card_appear_interval: int
    suffix_text: str = "人在投喂"
    reset_cnt: int
    display_flag: int
    gift_id: int
    gift_alert_message: str = "投喂一个%s支持主播"


class Data105Data(BaseModel):
    fade_duration: int
    cnt: int
    card_appear_interval: int
    suffix_text: str = '人分享了直播间'
    reset_cnt: int
    display_flag: int


class Data106Data(BaseModel):
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
    dmscore: int = 0


class Data102(Data):
    type: Literal[102]
    data: Data102Data

    validate_extra = field_validator('data', mode='before')(strange_dict)


class Data103(Data):
    type: Literal[103]
    data: Data103Data

    validate_extra = field_validator('data', mode='before')(strange_dict)


class Data104(Data):
    type: Literal[104]
    data: Data104Data

    validate_extra = field_validator('data', mode='before')(strange_dict)


class Data105(Data):
    type: Literal[105]
    data: Data105Data

    validate_extra = field_validator('data', mode='before')(strange_dict)


class Data106(Data):
    type: Literal[106]
    data: Data106Data

    validate_extra = field_validator('data', mode='before')(strange_dict)


class DmInteractionCommand(CommandModel):
    cmd: Literal['DM_INTERACTION']
    data: Annotated[Data102 | Data103 | Data104 | Data105 | Data106, Field(discriminator='type')]
