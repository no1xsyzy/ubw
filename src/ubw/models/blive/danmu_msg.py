from ._base import *


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


class DanmakuInfoModeInfoExtraIconPrefix(BaseModel):
    type: int
    resource: str


class DanmakuInfoModeInfoExtraIcon(BaseModel):
    prefix: DanmakuInfoModeInfoExtraIconPrefix


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
    id_str: str | None = None
    icon: DanmakuInfoModeInfoExtraIcon | None = None
    show_reply: bool = False
    reply_mid: int = 0
    reply_uname: str = ''
    reply_uname_color: str = ''
    reply_is_mystery: bool = False
    hit_combo: int = 0


class DanmakuInfoModeInfo(BaseModel):
    mode: int | None = None
    show_player_type: int | None = None
    extra: DanmakuInfoModeInfoExtra | None = None
    user: Uinfo | None = None

    validate_extra = field_validator('extra', mode='before')(strange_dict)


class DanmakuAggre(BaseModel):
    activity_identity: str = ""
    activity_source: int = 0
    not_show: int = 0


class DanmakuInfo(BaseModel):
    """弹幕消息
    :var mode: 采集自 .info[0][1] 弹幕显示模式， 1代表滚动 4代表底部
    :var font_size: 采集自 .info[0][2] 字体大小
    :var color: 采集自 .info[0][3] 弹幕字体颜色
    :var timestamp: 采集自 .info[0][4] 发送时间
    :var rnd: 采集自 .info[0][5] 这是每一个终端单独拥有的一个“随机数”，用以保证自己发送的弹幕在同终端上不会重复。
    可以注意到为了保证反应速度，发送弹幕时会即刻显示到弹幕栏。我们需要在同终端上去重但不同终端也要保证显示，这个“随机数”就是当前终端的标志。
    实际操作中它并不是一个随机数而是某一时刻的时间戳。
    :var uid_crc32: 采集自 .info[0][7] 用户ID文本CRC32校验
    :var msg_type: 采集自 .info[0][9] 是否礼物弹幕（节奏风暴）
    :var bubble_type: 采集自 .info[0][10] 右侧评论栏气泡类型
    :var bubble_color: 采集自 .info[0][11] 右侧评论栏气泡颜色，形如 "#1453BAFF,#4C2263A2,#3353BAFF"
    :var dm_type: 采集自 .info[0][12] 弹幕类型，0文本，1表情，2语音
    :var emoticon_options: 采集自 .info[0][13] 表情参数
    :var voice_config: 采集自 .info[0][14] 语音参数
    :var mode_info: 采集自 .info[0][15] 附加参数
    :var aggre: 采集自 .info[0][16] TODO：可能是聚合弹幕
    :var bubble_id: 采集自 .info[0][17] 右侧评论栏气泡相关信息，似乎 43代表舰长 42代表提督  TODO：还存在4但含义不明，与实际情况作过比对但也没有发现
    :var msg: 弹幕内容
    :var uid: 用户ID
    :var uname: 用户名
    :var admin: 是否房管
    :var vip: 是否月费老爷
    :var svip: 是否年费老爷
    :var urank: 用户身份，用来判断是否正式会员，猜测非正式会员为5000，正式会员为10000
    :var mobile_verify: 是否绑定手机
    :var uname_color: 用户名颜色
    :var medal_info: 粉丝牌信息
    :var user_level: 用户等级
    :var ulevel_color: 用户等级颜色
    :var ulevel_rank: 用户等级排名，>50000时为'>50000'
    :var old_title: 旧头衔
    :var title: 头衔
    :var privilege_type: 舰队类型，0非舰队，1总督，2提督，3舰长
    :var wealth_level: 荣耀等级
    :var group_medal: GroupMedal
    """

    mode: int
    font_size: int
    color: Color
    timestamp: datetime
    rnd: int
    uid_crc32: str
    msg_type: int
    bubble_type: int
    bubble_color: str | None = None
    dm_type: int
    emoticon_options: DanmakuInfoEmoticonOptions
    voice_config: dict
    mode_info: DanmakuInfoModeInfo
    aggre: DanmakuAggre | None = None
    bubble_id: int | None = None

    msg: str

    uid: int
    uname: str
    admin: bool
    vip: bool
    svip: bool
    urank: int
    mobile_verify: int
    uname_color: str

    medal_info: MedalInfo | None = None
    user_level: int
    ulevel_color: Color
    ulevel_rank: int | Literal['>50000']
    old_title: str
    title: str
    privilege_type: int
    wealth_level: int | None = None
    group_medal: GroupMedal | None = None

    # validators
    validate_emoticon_options = field_validator('emoticon_options', mode='before')(strange_dict)
    validate_voice_config = field_validator('voice_config', mode='before')(strange_dict)


def parse_medal_info(v3):
    if v3:
        return MedalInfo(
            medal_level=v3[0],
            medal_name=v3[1],
            anchor_uname=v3[2],
            anchor_roomid=v3[3],
            medal_color=v3[4],
            special=v3[5],
            icon_id=v3[6],
            medal_color_border=v3[7],
            medal_color_start=v3[8],
            medal_color_end=v3[9],
            guard_level=v3[10],
            is_lighted=v3[11],
            target_id=v3[12],
        )
    else:
        return None


def parse_group_medal(v17):
    if v17 is None:
        return None
    else:
        return GroupMedal(
            medal_id=v17[0],
            name=v17[1],
            is_lighted=v17[2],
        )


def parse_danmaku_info(v):
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
        "msg_type": v[0][9] or 0,
        "bubble_type": v[0][10] or 0,
        'bubble_color': v[0][11],
        "dm_type": v[0][12],
        "emoticon_options": v[0][13],
        "voice_config": v[0][14],
        "mode_info": v[0][15],
        'aggre': v[0][16],
        'bubble_id': v[0][17],

        "msg": v[1],

        "uid": v[2][0],
        "uname": v[2][1],
        "admin": v[2][2],
        "vip": v[2][3],
        "svip": v[2][4],
        "urank": v[2][5],
        "mobile_verify": v[2][6],
        "uname_color": v[2][7],  # 似乎与舰有关

        'medal_info': parse_medal_info(v[3]),

        "user_level": v[4][0] if v[4] else 0,
        # 4.1 always 0?
        "ulevel_color": v[4][2] if v[4] else 0xffffff,
        "ulevel_rank": v[4][3] if v[4] else ">50000",
        # 4.4 always 0?

        "old_title": v[5][0] if v[5] else "",
        "title": v[5][1] if v[5] else "",

        # .6
        "privilege_type": v[7],
        # .8
        # .9 validation { "ts": int maybe datetime, "ct": hex str upper, not CRC32. Or is? }
        # .10
        # .11
        # .12
        # .13
        # .14 lpl 这与 LPL 联赛有关吗？
        # .15 score 一个 int，对相同用户更经常是相同的，对不同用户通常是不同的，但都不绝对
        'wealth_level': v[16][0],
        'group_medal': parse_group_medal(v[17]) if len(v) > 17 else None,
    }


class DanmakuCommand(CommandModel):
    cmd: Literal['DANMU_MSG']
    info: DanmakuInfo
    dm_v2: str | None = None

    def summarize(self) -> Summary:
        return Summary(
            t=self.info.timestamp,
            msg=self.info.msg,
            user=(self.info.uid, self.info.uname),
            raw=self,
        )

    @field_validator('info', mode='before')
    def parse_danmaku_info(cls, v):
        if not isinstance(v, list):
            return v
        return parse_danmaku_info(v)


class Danmaku371111Command(DanmakuCommand):
    cmd: Literal['DANMU_MSG:3:7:1:1:1:1']
