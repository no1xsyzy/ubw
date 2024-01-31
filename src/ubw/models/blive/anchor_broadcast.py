from ._base import *


class ButtonInfo(BaseModel):
    blink_button_extra: str
    blink_button_label: int
    blink_button_target: str
    blink_button_type: str
    button_name: str
    hime_button_extra: str
    hime_button_h5_type: str
    hime_button_label: int
    hime_button_target: str
    hime_button_type: str


class Data(BaseModel):
    button_info: ButtonInfo
    milestone_index: int
    milestone_type: str
    milestone_value: int
    msg: str
    platform: int
    sender: str


class AnchorBroadcastCommand(CommandModel):
    cmd: Literal['ANCHOR_BROADCAST']
    data: Data
