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
    :var rnd: 这是每一个终端单独拥有的一个随机数，用以保证自己发送的弹幕在同终端上不会重复。 TODO：这是发送弹幕时即包含的吗？
    :var bubble_type: 右侧评论栏气泡类型
    :var bubble_color: 右侧评论栏气泡颜色，形如 "#1453BAFF,#4C2263A2,#3353BAFF"
    :var bubble_id: 右侧评论栏气泡相关信息，似乎 43=舰 42=提
    """

    mode: int
    """弹幕显示模式（滚动、顶部、底部）"""
    font_size: int
    """字体尺寸"""
    color: Color
    """颜色"""
    timestamp: datetime
    """时间戳（毫秒）"""
    rnd: int
    uid_crc32: str
    """用户ID文本的CRC32"""
    msg_type: int
    """是否礼物弹幕（节奏风暴）"""
    bubble_type: int
    bubble_color: str
    dm_type: int
    """弹幕类型，0文本，1表情，2语音"""
    emoticon_options: DanmakuInfoEmoticonOptions
    """表情参数"""
    voice_config: dict
    """语音参数"""
    mode_info: DanmakuInfoModeInfo
    """一些附加参数"""
    aggre: DanmakuAggre
    bubble_id: int

    msg: str
    """弹幕内容"""

    uid: int
    """用户ID"""
    uname: str
    """用户名"""
    admin: bool
    """是否房管"""
    vip: bool
    """是否月费老爷"""
    svip: bool
    """是否年费老爷"""
    urank: int
    """用户身份，用来判断是否正式会员，猜测非正式会员为5000，正式会员为10000"""
    mobile_verify: int
    """是否绑定手机"""
    uname_color: str
    """用户名颜色"""

    medal_info: MedalInfo | None = None

    user_level: int
    """用户等级"""
    ulevel_color: Color
    """用户等级颜色"""
    ulevel_rank: int | Literal['>50000']
    """用户等级排名，>50000时为'>50000'"""

    old_title: str
    """旧头衔"""
    title: str
    """头衔"""

    privilege_type: int
    """舰队类型，0非舰队，1总督，2提督，3舰长"""

    wealth_level: int | None = None
    """荣耀等级"""

    group_medal: GroupMedal | None = None

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
    def parse_dankamu_info(cls, v):
        if not isinstance(v, list):
            return v

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
            "bubble_type": v[0][10],
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

            "user_level": v[4][0],
            "ulevel_color": v[4][2],
            "ulevel_rank": v[4][3],

            "old_title": v[5][0],
            "title": v[5][1],

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
            'group_medal': parse_group_medal(v[17]),
        }


class Danmaku371111Command(DanmakuCommand):
    cmd: Literal['DANMU_MSG:3:7:1:1:1:1']

    @field_validator('info', mode='before')
    def parse_dankamu_info(cls, v):
        if isinstance(v, list):
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
                "msg_type": 0,
                "bubble_type": 0,
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
                "uname_color": v[2][7],

                'medal_info': parse_medal_info(v[3]),

                "user_level": 0,
                "ulevel_color": 0xffffff,
                "ulevel_rank": ">50000",

                "old_title": "",
                "title": "",

                "privilege_type": v[7],

                'wealth_level': v[16][0],
                'group_medal': parse_group_medal(v[17]),
            }
        return v
