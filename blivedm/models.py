# -*- coding: utf-8 -*-
import json
from typing import *

from pydantic import BaseModel

__all__ = (
    'HeartbeatMessage',
    'DanmakuMessage',
    'GiftMessage',
    'GuardBuyMessage',
    'SuperChatMessage',
    'SuperChatDeleteMessage',
)


class CommandModel(BaseModel):
    cmd: str


class HeartbeatMessage:
    """
    心跳消息

    :param popularity: 人气值
    """

    def __init__(
        self,
        popularity: int = None,
    ):
        self.popularity: int = popularity

    @classmethod
    def from_command(cls, data: dict):
        return cls(
            popularity=data['popularity'],
        )


class DanmakuMessage:
    """
    弹幕消息

    :param mode: 弹幕显示模式（滚动、顶部、底部）
    :param font_size: 字体尺寸
    :param color: 颜色
    :param timestamp: 时间戳（毫秒）
    :param rnd: 随机数，前端叫作弹幕ID，可能是去重用的
    :param uid_crc32: 用户ID文本的CRC32
    :param msg_type: 是否礼物弹幕（节奏风暴）
    :param bubble: 右侧评论栏气泡
    :param dm_type: 弹幕类型，0文本，1表情，2语音
    :param emoticon_options: 表情参数
    :param voice_config: 语音参数
    :param mode_info: 一些附加参数

    :param msg: 弹幕内容

    :param uid: 用户ID
    :param uname: 用户名
    :param admin: 是否房管
    :param vip: 是否月费老爷
    :param svip: 是否年费老爷
    :param urank: 用户身份，用来判断是否正式会员，猜测非正式会员为5000，正式会员为10000
    :param mobile_verify: 是否绑定手机
    :param uname_color: 用户名颜色

    :param medal_level: 勋章等级
    :param medal_name: 勋章名
    :param runame: 勋章房间主播名
    :param medal_room_id: 勋章房间ID
    :param mcolor: 勋章颜色
    :param special_medal: 特殊勋章

    :param user_level: 用户等级
    :param ulevel_color: 用户等级颜色
    :param ulevel_rank: 用户等级排名，>50000时为'>50000'

    :param old_title: 旧头衔
    :param title: 头衔

    :param privilege_type: 舰队类型，0非舰队，1总督，2提督，3舰长
    """

    def __init__(
        self,
        mode: int = None,
        font_size: int = None,
        color: int = None,
        timestamp: int = None,
        rnd: int = None,
        uid_crc32: str = None,
        msg_type: int = None,
        bubble: int = None,
        dm_type: int = None,
        emoticon_options: Union[dict, str] = None,
        voice_config: Union[dict, str] = None,
        mode_info: dict = None,

        msg: str = None,

        uid: int = None,
        uname: str = None,
        admin: int = None,
        vip: int = None,
        svip: int = None,
        urank: int = None,
        mobile_verify: int = None,
        uname_color: str = None,

        medal_level: str = None,
        medal_name: str = None,
        runame: str = None,
        medal_room_id: int = None,
        mcolor: int = None,
        special_medal: str = None,

        user_level: int = None,
        ulevel_color: int = None,
        ulevel_rank: str = None,

        old_title: str = None,
        title: str = None,

        privilege_type: int = None,
    ):
        self.mode: int = mode
        self.font_size: int = font_size
        self.color: int = color
        self.timestamp: int = timestamp
        self.rnd: int = rnd
        self.uid_crc32: str = uid_crc32
        self.msg_type: int = msg_type
        self.bubble: int = bubble
        self.dm_type: int = dm_type
        self.emoticon_options: Union[dict, str] = emoticon_options
        self.voice_config: Union[dict, str] = voice_config
        self.mode_info: dict = mode_info

        self.msg: str = msg

        self.uid: int = uid
        self.uname: str = uname
        self.admin: int = admin
        self.vip: int = vip
        self.svip: int = svip
        self.urank: int = urank
        self.mobile_verify: int = mobile_verify
        self.uname_color: str = uname_color

        self.medal_level: str = medal_level
        self.medal_name: str = medal_name
        self.runame: str = runame
        self.medal_room_id: int = medal_room_id
        self.mcolor: int = mcolor
        self.special_medal: str = special_medal

        self.user_level: int = user_level
        self.ulevel_color: int = ulevel_color
        self.ulevel_rank: str = ulevel_rank

        self.old_title: str = old_title
        self.title: str = title

        self.privilege_type: int = privilege_type

    @classmethod
    def from_command(cls, info: dict):
        if len(info[3]) != 0:
            medal_level = info[3][0]
            medal_name = info[3][1]
            runame = info[3][2]
            room_id = info[3][3]
            mcolor = info[3][4]
            special_medal = info[3][5]
        else:
            medal_level = 0
            medal_name = ''
            runame = ''
            room_id = 0
            mcolor = 0
            special_medal = 0

        return cls(
            mode=info[0][1],
            font_size=info[0][2],
            color=info[0][3],
            timestamp=info[0][4],
            rnd=info[0][5],
            uid_crc32=info[0][7],
            msg_type=info[0][9],
            bubble=info[0][10],
            dm_type=info[0][12],
            emoticon_options=info[0][13],
            voice_config=info[0][14],
            mode_info=info[0][15],

            msg=info[1],

            uid=info[2][0],
            uname=info[2][1],
            admin=info[2][2],
            vip=info[2][3],
            svip=info[2][4],
            urank=info[2][5],
            mobile_verify=info[2][6],
            uname_color=info[2][7],

            medal_level=medal_level,
            medal_name=medal_name,
            runame=runame,
            medal_room_id=room_id,
            mcolor=mcolor,
            special_medal=special_medal,

            user_level=info[4][0],
            ulevel_color=info[4][2],
            ulevel_rank=info[4][3],

            old_title=info[5][0],
            title=info[5][1],

            privilege_type=info[7],
        )

    @property
    def emoticon_options_dict(self) -> dict:
        """
        示例：
        {'bulge_display': 0, 'emoticon_unique': 'official_13', 'height': 60, 'in_player_area': 1, 'is_dynamic': 1,
         'url': 'https://i0.hdslb.com/bfs/live/a98e35996545509188fe4d24bd1a56518ea5af48.png', 'width': 183}
        """
        if isinstance(self.emoticon_options, dict):
            return self.emoticon_options
        try:
            return json.loads(self.emoticon_options)
        except (json.JSONDecodeError, TypeError):
            return {}

    @property
    def voice_config_dict(self) -> dict:
        """
        示例：
        {'voice_url': 'https%3A%2F%2Fboss.hdslb.com%2Flive-dm-voice%2Fb5b26e48b556915cbf3312a59d3bb2561627725945.wav
         %3FX-Amz-Algorithm%3DAWS4-HMAC-SHA256%26X-Amz-Credential%3D2663ba902868f12f%252F20210731%252Fshjd%252Fs3%25
         2Faws4_request%26X-Amz-Date%3D20210731T100545Z%26X-Amz-Expires%3D600000%26X-Amz-SignedHeaders%3Dhost%26
         X-Amz-Signature%3D114e7cb5ac91c72e231c26d8ca211e53914722f36309b861a6409ffb20f07ab8',
         'file_format': 'wav', 'text': '汤，下午好。', 'file_duration': 1}
        """
        if isinstance(self.voice_config, dict):
            return self.voice_config
        try:
            return json.loads(self.voice_config)
        except (json.JSONDecodeError, TypeError):
            return {}


class GiftMessage(BaseModel):
    """礼物消息"""
    giftName: str = None  # 礼物名
    num: int = None  # 数量
    uname: str = None  # 用户名
    face: str = None  # 用户头像URL
    guard_level: int = None  # 舰队等级，0非舰队，1总督，2提督，3舰长
    uid: int = None  # 用户ID
    timestamp: int = None  # 时间戳
    giftId: int = None  # 礼物ID
    giftType: int = None  # 礼物类型（未知）
    action: str = None  # 目前遇到的有'喂食'、'赠送'
    price: int = None  # 礼物单价瓜子数
    rnd: str = None  # 随机数，可能是去重用的。有时是时间戳+去重ID，有时是UUID
    coin_type: str = None  # 瓜子类型，'silver'或'gold'，1000金瓜子 = 1元
    total_coin: int = None  # 总瓜子数
    tid: str = None  # 可能是事务ID，有时和rnd相同


class GiftCommand(CommandModel):
    cmd: Literal['SEND_GIFT']
    data: GiftMessage


class GuardBuyMessage(BaseModel):
    """上舰消息"""
    uid: int = None  # 用户ID
    username: str = None  # 用户名
    guard_level: int = None  # 舰队等级，0非舰队，1总督，2提督，3舰长
    num: int = None  # 数量
    price: int = None  # 单价金瓜子数
    gift_id: int = None  # 礼物ID
    gift_name: str = None  # 礼物名
    start_time: int = None  # 开始时间戳，和结束时间戳相同
    end_time: int = None  # 结束时间戳，和开始时间戳相同结束时间戳，和开始时间戳相同


class GuardBuyCommand(CommandModel):
    cmd: Literal['GUARD_BUY']
    data: GuardBuyMessage


class GiftInfo(BaseModel):
    gift_id: int = None  # 礼物ID
    gift_name: str = None  # 礼物名


class UserInfo(BaseModel):
    uname: str = None  # 用户名
    face: str = None  # 用户头像URL
    guard_level: int = None  # 舰队等级，0非舰队，1总督，2提督，3舰长
    user_level: int = None  # 用户等级


class SuperChatMessage(BaseModel):
    """醒目留言消息"""
    price: int = None  # 价格（人民币）
    message: str = None  # 消息
    message_trans: Optional[str] = None  # 消息日文翻译（目前只出现在SUPER_CHAT_MESSAGE_JPN）
    start_time: int = None  # 开始时间戳
    end_time: int = None  # 结束时间戳
    time: int = None  # 剩余时间（约等于 结束时间戳 - 开始时间戳）
    id: int = None  # 醒目留言ID，删除时用
    gift: GiftInfo
    uid: int = None  # 用户ID
    user_info: UserInfo
    background_bottom_color: str = None  # 底部背景色，'#rrggbb'
    background_color: str = None  # 背景色，'#rrggbb'
    background_icon: str = None  # 背景图标
    background_image: str = None  # 背景图URL
    background_price_color: str = None  # 背景价格颜色，'#rrggbb'


class SuperChatCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE']
    data: SuperChatMessage


class SuperChatDeleteMessage(BaseModel):
    """删除醒目留言消息"""
    ids: List[int]  # 醒目留言ID数组


class SuperChatDeleteCommand(CommandModel):
    title: Literal['SUPER_CHAT_MESSAGE_DELETE']
    data: SuperChatDeleteMessage


class RoomChangeMessage(BaseModel):
    """直播间信息修改"""
    title: str
    area_id: int
    parent_area_id: int
    area_name: str
    parent_area_name: str
    live_key: str
    sub_session_key: str


class RoomChangeCommand(CommandModel):
    cmd: Literal['ROOM_CHANGE']
    data: RoomChangeMessage


class LiveCommand(CommandModel):
    """开播"""
    cmd: Literal['LIVE']
    live_key: str
    voice_background: str
    sub_session_key: str
    live_platform: str
    live_model: int
    roomid: int


class PreparingCommand(CommandModel):
    """下播"""
    cmd: Literal['PREPARING']
    roomid: int
