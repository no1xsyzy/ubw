from ._base import *


class Gift(BaseModel):
    gift_id: int
    gift_name: str
    num: int


class MedalInfo(BaseModel):
    anchor_roomid: int
    anchor_uname: str
    icon_id: int
    medal_color: Color | str
    medal_level: int
    medal_name: str
    special: str
    target_id: int


class UserInfo(BaseModel):
    face: str
    face_frame: str
    guard_level: int
    is_main_vip: int
    is_svip: int
    is_vip: int
    level_color: Color
    manager: int
    title: str
    uname: str
    user_level: int


class Data(BaseModel):
    background_bottom_color: Color
    background_color: Color
    background_icon: str
    background_image: str
    background_price_color: Color
    end_time: datetime
    gift: Gift
    id: str
    is_ranked: int
    medal_info: MedalInfo | None
    message: str
    message_jpn: str
    price: int
    "RMB"
    rate: int
    start_time: datetime
    time: int
    "秒"
    token: str
    ts: datetime
    uid: str
    user_info: UserInfo


class SuperChatMessageJpnCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE_JPN']
    roomid: int
    data: Data
