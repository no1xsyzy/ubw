# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime, timedelta, timezone
from typing import *

from pydantic import BaseModel, validator, root_validator, Field


class Scatter(BaseModel):
    min: int
    max: int


class CommandModel(BaseModel):
    cmd: str
    ct: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(seconds=8 * 3600))))

    class Config:
        extra = 'forbid'


class HeartbeatMessage(BaseModel):
    """心跳消息"""

    popularity: int
    """人气值"""


class HeartbeatCommand(CommandModel):
    cmd: Literal['_HEARTBEAT']
    data: HeartbeatMessage


class Color(BaseModel):
    __root__: Union[str, int]

    @root_validator(pre=True)
    def parse_color(cls, values):
        data = values['__root__']
        if isinstance(data, str) and data.startswith("#"):
            data = data.lstrip("#")
            if len(data) == 3:
                r, g, b = data
                data = r + r + g + g + b + b
        elif isinstance(data, int):
            data = ("000000" + hex(data)[2:])[-6:]
        if re.match("[0-9a-fA-F]{6}", data):
            return {'__root__': data}
        else:
            raise ValueError(f"`{values['__root__']}` is not a valid color")

    @property
    def hashcolor(self):
        return "#" + self.__root__

    @property
    def contrast_black_or_white(self):
        return 'black' if max(self.red, self.green, self.blue) > 127 else 'white'

    @property
    def red(self):
        return int(self.__root__[:2], 16)

    @property
    def green(self):
        return int(self.__root__[2:4], 16)

    @property
    def blue(self):
        return int(self.__root__[4:], 16)

    def __str__(self):
        return "#" + self.__root__


def strange_dict(cls, v):
    try:
        if not isinstance(v, dict):
            v = json.loads(v)
        if not v:
            return {}
        return v
    except (json.JSONDecodeError, TypeError):
        return {}


class DanmakuInfoEmoticonOptions(BaseModel):
    bulge_display: int | None = None
    emoticon_unique: str | None = None
    height: int | None = None
    in_player_area: int | None = None
    is_dynamic: int | None = None
    url: str | None = None
    width: int | None = None


class DanmakuInfoModeInfoExtraEmot(BaseModel):
    emoticon_id: int | None = None
    emoji: str | None = None
    descript: str | None = None
    url: str | None = None
    width: int | None = None
    height: int | None = None
    emoticon_unique: str | None = None
    count: int | None = None


class DanmakuInfoModeInfoExtra(BaseModel):
    send_from_me: bool | None = None
    mode: int | None = None
    color: Color | None = None
    dm_type: int | None = None
    font_size: int | None = None
    player_mode: int | None = None
    show_player_type: int | None = None
    content: str | None = None
    user_hash: str | None = None
    emoticon_unique: str | None = None
    bulge_display: int | None = None
    recommend_score: int | None = None
    main_state_dm_color: str | None = None
    objective_state_dm_color: str | None = None
    direction: int | None = None
    pk_direction: int | None = None
    quartet_direction: int | None = None
    anniversary_crowd: int | None = None
    yeah_space_type: str | None = None
    yeah_space_url: str | None = None
    jump_to_url: str | None = None
    space_type: str | None = None
    space_url: str | None = None
    animation: dict | None = None
    emots: dict[str, DanmakuInfoModeInfoExtraEmot] | None = None
    is_audited: bool | None = None


class DanmakuInfoModeInfo(BaseModel):
    mode: int | None = None
    show_player_type: int | None = None
    extra: DanmakuInfoModeInfoExtra | None = None

    validate_extra = validator('extra', pre=True, allow_reuse=True)(strange_dict)


class DanmakuInfo(BaseModel):
    """弹幕消息"""

    mode: int
    """弹幕显示模式（滚动、顶部、底部）"""
    font_size: int
    """字体尺寸"""
    color: int
    """颜色"""
    timestamp: datetime
    """时间戳（毫秒）"""
    rnd: int
    """随机数，前端叫作弹幕ID，可能是去重用的"""
    uid_crc32: str
    """用户ID文本的CRC32"""
    msg_type: int
    """是否礼物弹幕（节奏风暴）"""
    bubble: int
    """右侧评论栏气泡"""
    dm_type: int
    """弹幕类型，0文本，1表情，2语音"""
    emoticon_options: DanmakuInfoEmoticonOptions
    """表情参数"""
    voice_config: dict
    """语音参数"""
    mode_info: DanmakuInfoModeInfo
    """一些附加参数"""

    msg: str
    """弹幕内容"""

    uid: int
    """用户ID"""
    uname: str
    """用户名"""
    admin: int
    """是否房管"""
    vip: int
    """是否月费老爷"""
    svip: int
    """是否年费老爷"""
    urank: int
    """用户身份，用来判断是否正式会员，猜测非正式会员为5000，正式会员为10000"""
    mobile_verify: int
    """是否绑定手机"""
    uname_color: str
    """用户名颜色"""

    medal_level: str
    """勋章等级"""
    medal_name: str
    """勋章名"""
    runame: str
    """勋章房间主播名"""
    medal_room_id: int
    """勋章房间ID"""
    mcolor: int
    """勋章颜色"""
    special_medal: str
    """特殊勋章"""

    user_level: int
    """用户等级"""
    ulevel_color: int
    """用户等级颜色"""
    ulevel_rank: str
    """用户等级排名，>50000时为'>50000'"""

    old_title: str
    """旧头衔"""
    title: str
    """头衔"""

    privilege_type: int
    """舰队类型，0非舰队，1总督，2提督，3舰长"""

    validate_emoticon_options = validator('emoticon_options', pre=True, allow_reuse=True)(strange_dict)

    validate_voice_config = validator('voice_config', pre=True, allow_reuse=True)(strange_dict)


class DanmakuCommand(CommandModel):
    cmd: Literal['DANMU_MSG']
    info: DanmakuInfo
    dm_v2: str | None = None

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
                # .0.0
                "mode": v[0][1],
                "font_size": v[0][2],
                "color": v[0][3],
                "timestamp": v[0][4],
                "rnd": v[0][5],
                # .0.6
                "uid_crc32": v[0][7],
                # .0.8
                "msg_type": v[0][9],
                "bubble": v[0][10],
                # .0.11
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
    giftName: str
    """礼物名"""
    num: int
    """数量"""
    uname: str
    """用户名"""
    face: str
    """用户头像URL"""
    guard_level: int
    """舰队等级，0非舰队，1总督，2提督，3舰长"""
    uid: int
    """用户ID"""
    timestamp: datetime
    """时间戳"""
    giftId: int
    """礼物ID"""
    giftType: int
    """礼物类型（未知）"""
    action: str
    """目前遇到的有'喂食'、'赠送'"""
    price: int
    """礼物单价瓜子数"""
    rnd: str
    """随机数，可能是去重用的。有时是时间戳+去重ID，有时是UUID"""
    coin_type: str
    """瓜子类型，'silver'或'gold'，1000金瓜子 = 1元"""
    total_coin: int
    """总瓜子数"""
    tid: str
    """可能是事务ID，有时和rnd相同"""


class GiftCommand(CommandModel):
    cmd: Literal['SEND_GIFT']
    data: GiftMessage


class GuardBuyMessage(BaseModel):
    """上舰消息"""
    uid: int
    """用户ID"""
    username: str
    """用户名"""
    guard_level: int
    """舰队等级，0非舰队，1总督，2提督，3舰长"""
    num: int
    """数量"""
    price: int
    """单价金瓜子数"""
    gift_id: int
    """礼物ID"""
    gift_name: str
    """礼物名"""
    start_time: datetime
    """开始时间戳，和结束时间戳相同"""
    end_time: datetime
    """结束时间戳，和开始时间戳相同"""


class GuardBuyCommand(CommandModel):
    cmd: Literal['GUARD_BUY']
    data: GuardBuyMessage


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


class SuperChatDeleteMessage(BaseModel):
    """删除醒目留言消息"""
    ids: list[int]
    """醒目留言ID数组"""


class SuperChatDeleteCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE_DELETE']
    data: SuperChatDeleteMessage
    roomid: int


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
    live_time: datetime | None = None
    roomid: int


class PreparingCommand(CommandModel):
    """下播"""
    cmd: Literal['PREPARING']
    roomid: int
    scatter: Scatter | None = None


class WarningCommand(CommandModel):
    """超管警告"""
    cmd: Literal['WARNING']
    msg: str
    roomid: int


class HotRankSettlementData(BaseModel):
    rank: int
    """排名"""
    uname: str
    """主播用户名"""
    face: str
    """主播头像"""
    timestamp: datetime
    """达成时间"""
    icon: str
    """榜单图标"""
    area_name: str
    """榜单名称"""
    url: str
    cache_key: str
    dm_msg: str
    """文字描述"""
    dmscore: int | None = None


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
    buttonText: str | None = None


class SkinConfig(BaseModel):
    android: Dict[str, ZipSkin]
    ios: Dict[str, ZipSkin]
    ipad: Dict[str, ZipSkin]
    web: Dict[str, WebSkin]


class RoomSkinCommand(CommandModel):
    cmd: Literal['ROOM_SKIN_MSG']
    skin_id: int
    status: int
    end_time: datetime
    current_time: datetime
    only_local: bool
    skin_config: SkinConfig
    scatter: Scatter


class TradingScoreData(BaseModel):
    bubble_show_time: timedelta
    num: int
    score_id: int
    uid: int
    update_time: datetime
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


class RingStatusChangeData(BaseModel):
    status: int


class RingStatusChangeCommand(CommandModel):
    cmd: Literal['RING_STATUS_CHANGE']
    data: RingStatusChangeData


class RingStatusChangeCommandV2(CommandModel):
    cmd: Literal['RING_STATUS_CHANGE_V2']
    data: RingStatusChangeData


class LiveMultiViewChangeScatter(BaseModel):
    max: int
    min: int


class LiveMultiViewChangeData(BaseModel):
    scatter: LiveMultiViewChangeScatter


class LiveMultiViewChangeCommand(CommandModel):
    cmd: Literal['LIVE_MULTI_VIEW_CHANGE']
    data: LiveMultiViewChangeData


class DanmuNew(BaseModel):
    danmu: str
    danmu_view: str
    reject: bool


class AnchorLotStartData(BaseModel):
    asset_icon: str
    asset_icon_webp: str
    award_image: str
    award_name: str
    award_num: int
    award_type: int
    cur_gift_num: int
    current_time: datetime
    danmu: str
    danmu_new: list[DanmuNew]
    danmu_type: int
    gift_id: int
    gift_name: str
    gift_num: int
    gift_price: int
    goaway_time: str
    goods_id: int
    id: int
    is_broadcast: int
    join_type: int
    lot_status: int
    max_time: int
    require_text: str
    require_type: int
    require_value: int
    room_id: int
    send_gift_ensure: int
    show_panel: int
    start_dont_popup: int
    status: int
    time: int
    url: str
    web_url: str


class AnchorLotStartCommand(CommandModel):
    """天选时刻开始"""
    cmd: Literal['ANCHOR_LOT_START']
    data: AnchorLotStartData


class AwardUser(BaseModel):
    uid: int
    uname: str
    face: str
    level: int
    color: Color
    num: int


class AnchorLotAwardData(BaseModel):
    award_dont_popup: int
    award_image: str
    award_name: str
    award_num: int
    award_type: int
    award_users: list[AwardUser]
    id: int
    lot_status: int
    url: str
    web_url: str


class AnchorLotAwardCommand(CommandModel):
    """天选时刻中奖"""
    cmd: Literal['ANCHOR_LOT_AWARD']
    data: AnchorLotAwardData


class AnchorLotEndData(BaseModel):
    id: int


class AnchorLotEndCommand(CommandModel):
    """天选时刻结束"""
    cmd: Literal['ANCHOR_LOT_END']
    data: AnchorLotEndData


class AnchorLotCheckStatusData(BaseModel):
    id: int
    status: int
    uid: int
    """主播uid"""


class AnchorLotCheckStatusCommand(CommandModel):
    """天选时刻状态检查"""
    cmd: Literal['ANCHOR_LOT_CHECKSTATUS']
    data: AnchorLotCheckStatusData


class WidgetGiftStarProcess(BaseModel):
    gift_id: int
    gift_img: str
    gift_name: str
    completed_num: str
    target_num: str


class WidgetGiftStarProcessData(BaseModel):
    start_date: str
    process_list: list[WidgetGiftStarProcess]
    finished: bool
    ddl_timestamp: datetime
    version: datetime
    reward_gift: int
    reward_gift_img: str
    reward_gift_name: str


class WidgetGiftStarProcessCommand(CommandModel):
    cmd: Literal['WIDGET_GIFT_STAR_PROCESS']
    data: WidgetGiftStarProcessData


class WatchedChangeData(BaseModel):
    num: int
    text_small: str
    text_large: str


class WatchedChangeCommand(CommandModel):
    cmd: Literal['WATCHED_CHANGE']
    data: WatchedChangeData


class NoticeMsgCommand(CommandModel):
    cmd: Literal['NOTICE_MSG']
    id: int

    name: str
    msg_type: int
    """1:人气榜第一名
    2:3D小电视飞船专用
    2:大乱斗连胜人气红包"""

    full: dict
    half: dict
    side: dict
    roomid: int
    real_roomid: int
    msg_common: str
    msg_self: str
    link_url: str
    shield_uid: int
    business_id: str
    scatter: Scatter
    marquee_id: str
    notice_type: int


class OnlineRankCountData(BaseModel):
    count: int


class OnlineRankCountCommand(CommandModel):
    cmd: Literal['ONLINE_RANK_COUNT']
    data: OnlineRankCountData


class FansMedal(BaseModel):
    anchor_roomid: int
    guard_level: int
    icon_id: int
    is_lighted: int
    medal_color: Color
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    medal_name: str
    score: int
    special: str
    target_id: int


class Contribution(BaseModel):
    grade: int


class InteractWordData(BaseModel):
    contribution: Contribution
    core_user_type: int
    dmscore: int
    fans_medal: FansMedal
    identities: list[int]
    is_spread: int
    msg_type: int
    privilege_type: int
    score: datetime
    spread_desc: str
    spread_info: str
    tail_icon: int
    timestamp: datetime
    trigger_time: datetime
    uid: int
    uname: str
    uname_color: str


class InteractWordCommand(CommandModel):
    cmd: Literal['INTERACT_WORD']
    data: InteractWordData


class EntryEffectData(BaseModel):
    id: int
    uid: int
    target_id: int
    mock_effect: int
    face: str
    privilege_type: int
    copy_writing: str
    copy_color: Color
    priority: int
    basemap_url: str
    show_avatar: int
    effective_time: int
    web_basemap_url: str
    web_effective_time: int
    web_effect_close: int
    web_close_time: int
    business: int
    copy_writing_v2: str
    icon_list: list
    max_delay_time: int
    trigger_time: datetime
    identities: int
    effect_silent_time: int
    effective_time_new: int
    web_dynamic_url_webp: str
    web_dynamic_url_apng: str
    mobile_dynamic_url_webp: str


class EntryEffectCommand(CommandModel):
    cmd: Literal['ENTRY_EFFECT']
    data: EntryEffectData


class StopLiveRoomListData(BaseModel):
    room_id_list: list[int]


class StopLiveRoomListCommand(CommandModel):
    cmd: Literal['STOP_LIVE_ROOM_LIST']
    data: StopLiveRoomListData


class GuardHonorThousandData(BaseModel):
    add: list[int]
    del_: list[int] = Field(alias='del')


class GuardHonorThousandCommand(CommandModel):
    cmd: Literal['GUARD_HONOR_THOUSAND']
    data: GuardHonorThousandData


AnnotatedCommandModel = Annotated[Union[tuple(CommandModel.__subclasses__())], Field(discriminator='cmd')]

__all__ = ('CommandModel', *(cmdm.__name__ for cmdm in CommandModel.__subclasses__()), 'AnnotatedCommandModel')
