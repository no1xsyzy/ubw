from ._base import *


class UserInfo(BaseModel):
    uid: int
    uname: str


class ComboSendData(BaseModel):
    action: str
    """目前遇到的有'喂食'、'赠送'"""
    batch_combo_id: str
    batch_combo_num: int
    combo_id: str
    combo_num: int
    combo_total_coin: int
    dmscore: int
    gift_id: int
    gift_name: str
    gift_num: int
    is_join_receiver: bool
    is_naming: bool
    is_show: int
    medal_info: MedalInfo
    name_color: Color
    r_uname: str
    receive_user_info: UserInfo
    ruid: int
    send_master: None
    total_num: int
    uid: int
    uname: str


class ComboSendCommand(CommandModel):
    cmd: Literal['COMBO_SEND']
    data: ComboSendData
