from ._base import *


class SendMaster(BaseModel):
    room_id: int
    uid: int
    uname: str


class ComboEndData(BaseModel):
    uid: int
    ruid: int
    uname: str
    r_uname: str
    combo_num: int
    gift_id: int
    gift_num: int
    batch_combo_num: int
    gift_name: str
    action: str
    send_master: SendMaster | None
    price: int
    start_time: int
    end_time: int
    guard_level: int
    name_color: str
    combo_total_coin: int


class ComboEndCommand(CommandModel):
    cmd: Literal['COMBO_END']
    data: ComboEndData
