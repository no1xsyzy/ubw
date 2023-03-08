from ._base import *


class GiftInfo(BaseModel):
    gift_id: int
    """礼物ID"""
    gift_name: str
    """礼物名"""
    num: int


class UserInfo(BaseModel):
    uname: str
    """用户名"""
    face: str
    """用户头像URL"""
    face_frame: str
    guard_level: int
    """舰队等级，0非舰队，1总督，2提督，3舰长"""
    is_main_vip: int
    is_svip: int
    is_vip: int
    level_color: Color
    manager: int
    name_color: Color
    title: str
    user_level: int
    """用户等级"""


class MedalInfo(BaseModel):
    anchor_roomid: int
    """粉丝牌主播房间号"""
    anchor_uname: str
    """粉丝牌主播用户名"""
    guard_level: int
    """大航海等级"""
    icon_id: int
    is_lighted: int
    """点亮？"""
    medal_color: Color
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    """粉丝牌等级"""
    medal_name: str
    """粉丝牌名称"""
    special: str
    target_id: int
    """粉丝牌主播uid"""


class SuperChatMessage(BaseModel):
    """醒目留言消息"""
    price: int
    """价格（人民币）"""
    message: str
    """消息"""
    message_trans: str | None
    """消息日文翻译（目前只出现在SUPER_CHAT_MESSAGE_JPN）"""
    trans_mark: int

    start_time: datetime
    """开始时间戳"""
    ts: datetime
    """似乎与开始时间戳相同"""
    end_time: datetime
    """结束时间戳，秒"""
    time: timedelta
    """剩余时间（约等于 结束时间戳 - 开始时间戳）"""

    id: int
    """醒目留言ID，删除时用"""
    token: str
    is_ranked: int
    is_send_audit: int
    uid: int
    """用户ID"""
    gift: GiftInfo
    user_info: UserInfo
    background_bottom_color: Color
    """底部背景色"""
    background_color: Color
    """背景色"""
    background_color_start: Color
    background_color_end: Color
    background_icon: str
    """背景图标"""
    background_image: str
    """背景图URL"""
    background_price_color: Color
    """背景价格颜色"""
    message_font_color: Color
    rate: int
    color_point: float
    dmscore: int


class SuperChatCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE']
    data: SuperChatMessage
    roomid: int

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.start_time,
            msg=self.data.message,
            user=(self.data.uid, self.data.user_info.uname),
            room_id=self.roomid,
            price=self.data.price,
            raw=self,
        )
