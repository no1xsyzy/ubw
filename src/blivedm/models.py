# -*- coding: utf-8 -*-
import json
from typing import *

from pydantic import BaseModel, validator

__all__ = (
    'HeartbeatMessage',
    'DanmakuCommand',
    'GiftMessage',
    'GuardBuyMessage',
    'SuperChatMessage',
    'SuperChatDeleteMessage',
)


class CommandModel(BaseModel):
    cmd: str

    class Config:
        extra = 'forbid'


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


class DanmakuInfo(BaseModel):
    """
    弹幕消息
    """

    mode: int  # 弹幕显示模式（滚动、顶部、底部）
    font_size: int  # 字体尺寸
    color: int  # 颜色
    timestamp: int  # 时间戳（毫秒）
    rnd: int  # 随机数，前端叫作弹幕ID，可能是去重用的
    uid_crc32: str  # 用户ID文本的CRC32
    msg_type: int  # 是否礼物弹幕（节奏风暴）
    bubble: int  # 右侧评论栏气泡
    dm_type: int  # 弹幕类型，0文本，1表情，2语音
    emoticon_options: dict  # 表情参数
    voice_config: dict  # 语音参数
    mode_info: dict  # 一些附加参数

    msg: str  # 弹幕内容

    uid: int  # 用户ID
    uname: str  # 用户名
    admin: int  # 是否房管
    vip: int  # 是否月费老爷
    svip: int  # 是否年费老爷
    urank: int  # 用户身份，用来判断是否正式会员，猜测非正式会员为5000，正式会员为10000
    mobile_verify: int  # 是否绑定手机
    uname_color: str  # 用户名颜色

    medal_level: str  # 勋章等级
    medal_name: str  # 勋章名
    runame: str  # 勋章房间主播名
    medal_room_id: int  # 勋章房间ID
    mcolor: int  # 勋章颜色
    special_medal: str  # 特殊勋章

    user_level: int  # 用户等级
    ulevel_color: int  # 用户等级颜色
    ulevel_rank: str  # 用户等级排名，>50000时为'>50000'

    old_title: str  # 旧头衔
    title: str  # 头衔

    privilege_type: int  # 舰队类型，0非舰队，1总督，2提督，3舰长

    @validator('emoticon_options', pre=True)
    def emoticon_options_dict(cls, v):
        """
        示例：
        {'bulge_display': 0, 'emoticon_unique': 'official_13', 'height': 60, 'in_player_area': 1, 'is_dynamic': 1,
         'url': 'https://i0.hdslb.com/bfs/live/a98e35996545509188fe4d24bd1a56518ea5af48.png', 'width': 183}
        """
        if isinstance(v, dict):
            return v
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError):
            return {}

    @validator('voice_config', pre=True)
    def voice_config_dict(cls, v) -> dict:
        """
        示例：
        {'voice_url': 'https%3A%2F%2Fboss.hdslb.com%2Flive-dm-voice%2Fb5b26e48b556915cbf3312a59d3bb2561627725945.wav
         %3FX-Amz-Algorithm%3DAWS4-HMAC-SHA256%26X-Amz-Credential%3D2663ba902868f12f%252F20210731%252Fshjd%252Fs3%25
         2Faws4_request%26X-Amz-Date%3D20210731T100545Z%26X-Amz-Expires%3D600000%26X-Amz-SignedHeaders%3Dhost%26
         X-Amz-Signature%3D114e7cb5ac91c72e231c26d8ca211e53914722f36309b861a6409ffb20f07ab8',
         'file_format': 'wav', 'text': '汤，下午好。', 'file_duration': 1}
        """
        if isinstance(v, dict):
            return v
        try:
            return json.loads(v)
        except (json.JSONDecodeError, TypeError):
            return {}


class DanmakuCommand(CommandModel):
    cmd: Literal['DANMU_MSG']
    info: DanmakuInfo

    @validator('info', pre=True)
    def parse_dankamu_info(cls, v):
        if isinstance(v, list):
            if len(v[3]) != 0:
                medal_level = v[3][0]
                medal_name = v[3][1]
                runame = v[3][2]
                room_id = v[3][3]
                mcolor = v[3][4]
                special_medal = v[3][5]
            else:
                medal_level = 0
                medal_name = ''
                runame = ''
                room_id = 0
                mcolor = 0
                special_medal = 0

            return {
                "mode": v[0][1],
                "font_size": v[0][2],
                "color": v[0][3],
                "timestamp": v[0][4],
                "rnd": v[0][5],
                "uid_crc32": v[0][7],
                "msg_type": v[0][9],
                "bubble": v[0][10],
                "dm_type": v[0][12],
                "emoticon_options": v[0][13],
                "voice_config": v[0][14],
                "mode_info": v[0][15],

                "msg": v[1],

                "uid": v[2][0],
                "uname": v[2][1],
                "admin": v[2][2],
                "vip": v[2][3],
                "svip": v[2][4],
                "urank": v[2][5],
                "mobile_verify": v[2][6],
                "uname_color": v[2][7],

                "medal_level": medal_level,
                "medal_name": medal_name,
                "runame": runame,
                "medal_room_id": room_id,
                "mcolor": mcolor,
                "special_medal": special_medal,

                "user_level": v[4][0],
                "ulevel_color": v[4][2],
                "ulevel_rank": v[4][3],

                "old_title": v[5][0],
                "title": v[5][1],

                "privilege_type": v[7],
            }
        return v


class GiftMessage(BaseModel):
    """礼物消息"""
    giftName: str  # 礼物名
    num: int  # 数量
    uname: str  # 用户名
    face: str  # 用户头像URL
    guard_level: int  # 舰队等级，0非舰队，1总督，2提督，3舰长
    uid: int  # 用户ID
    timestamp: int  # 时间戳
    giftId: int  # 礼物ID
    giftType: int  # 礼物类型（未知）
    action: str  # 目前遇到的有'喂食'、'赠送'
    price: int  # 礼物单价瓜子数
    rnd: str  # 随机数，可能是去重用的。有时是时间戳+去重ID，有时是UUID
    coin_type: str  # 瓜子类型，'silver'或'gold'，1000金瓜子 = 1元
    total_coin: int  # 总瓜子数
    tid: str  # 可能是事务ID，有时和rnd相同


class GiftCommand(CommandModel):
    cmd: Literal['SEND_GIFT']
    data: GiftMessage


class GuardBuyMessage(BaseModel):
    """上舰消息"""
    uid: int  # 用户ID
    username: str  # 用户名
    guard_level: int  # 舰队等级，0非舰队，1总督，2提督，3舰长
    num: int  # 数量
    price: int  # 单价金瓜子数
    gift_id: int  # 礼物ID
    gift_name: str  # 礼物名
    start_time: int  # 开始时间戳，和结束时间戳相同
    end_time: int  # 结束时间戳，和开始时间戳相同


class GuardBuyCommand(CommandModel):
    cmd: Literal['GUARD_BUY']
    data: GuardBuyMessage


class GiftInfo(BaseModel):
    gift_id: int  # 礼物ID
    gift_name: str  # 礼物名


class UserInfo(BaseModel):
    uname: str  # 用户名
    face: str  # 用户头像URL
    guard_level: int  # 舰队等级，0非舰队，1总督，2提督，3舰长
    user_level: int  # 用户等级


class SuperChatMessage(BaseModel):
    """醒目留言消息"""
    price: int  # 价格（人民币）
    message: str  # 消息
    message_trans: Optional[str]  # 消息日文翻译（目前只出现在SUPER_CHAT_MESSAGE_JPN）
    start_time: int  # 开始时间戳
    end_time: int  # 结束时间戳
    time: int  # 剩余时间（约等于 结束时间戳 - 开始时间戳）
    id: int  # 醒目留言ID，删除时用
    gift: GiftInfo
    uid: int  # 用户ID
    user_info: UserInfo
    background_bottom_color: str  # 底部背景色，'#rrggbb'
    background_color: str  # 背景色，'#rrggbb'
    background_icon: str  # 背景图标
    background_image: str  # 背景图URL
    background_price_color: str  # 背景价格颜色，'#rrggbb'


class SuperChatCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE']
    data: SuperChatMessage


class SuperChatDeleteMessage(BaseModel):
    """删除醒目留言消息"""
    ids: list[int]  # 醒目留言ID数组


class SuperChatDeleteCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE_DELETE']
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


class WarningCommand(CommandModel):
    """超管警告"""
    cmd: Literal['WARNING']
    msg: str
    roomid: int


class HotRankSettlementData(BaseModel):
    rank: int  # 排名
    uname: str  # 主播用户名
    face: str  # 主播头像
    timestamp: int  # 达成时间
    icon: str  # 榜单图标
    area_name: str  # 榜单名称
    url: str
    cache_key: str
    dm_msg: str  # 文字描述
    dmscore: Optional[int] = None


class HotRankSettlementV2Command(CommandModel):
    cmd: Literal['HOT_RANK_SETTLEMENT_V2']
    data: HotRankSettlementData


class HotRankSettlementCommand(CommandModel):
    cmd: Literal['HOT_RANK_SETTLEMENT']
    data: HotRankSettlementData


class RoomBlockMsg(BaseModel):
    dmscore: int
    operator: int
    uid: int
    uname: str


class RoomBlockCommand(CommandModel):
    cmd: Literal['ROOM_BLOCK_MSG']
    data: RoomBlockMsg
    uid: str
    uname: str


class ZipSkin(BaseModel):
    zip: str
    md5: str


class WebSkin(BaseModel):
    zip: str
    md5: str
    platform: str
    version: str
    headInfoBgPic: str
    giftControlBgPic: str
    rankListBgPic: str
    mainText: str
    normalText: str
    highlightContent: str
    border: str
    buttonText: str


class SkinConfig(BaseModel):
    android: Dict[str, ZipSkin]
    ios: Dict[str, ZipSkin]
    ipad: Dict[str, ZipSkin]
    web: Dict[str, WebSkin]


class Scatter(BaseModel):
    min: int
    max: int


class RoomSkinCommand(CommandModel):
    cmd: Literal['ROOM_SKIN_MSG']
    skin_id: int
    status: int
    end_time: int
    current_time: int
    only_local: bool
    skin_config: SkinConfig
    scatter: Scatter


class TradingScoreData(BaseModel):
    bubble_show_time: int
    num: int
    score_id: int
    uid: int
    update_time: int
    update_type: int


class TradingScoreCommand(CommandModel):
    cmd: Literal['TRADING_SCORE']
    data: TradingScoreData


class RoomAdminsCommand(CommandModel):
    cmd: Literal['ROOM_ADMINS']
    uids: list[int]


class RoomAdminEntrance(CommandModel):
    cmd: Literal['room_admin_entrance']
    dmscore: int
    level: int
    msg: str
    uid: int
