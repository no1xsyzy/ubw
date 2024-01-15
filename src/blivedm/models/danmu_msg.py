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

    def summarize(self) -> Summary:
        return Summary(
            t=self.info.timestamp,
            msg=self.info.msg,
            user=(self.info.uid, self.info.uname),
            raw=self,
        )

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


class Danmaku371111Command(DanmakuCommand):
    cmd: Literal['DANMU_MSG:3:7:1:1:1:1']

    @validator('info', pre=True)
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
                "bubble": 0,
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

                "medal_level": 0,
                "medal_name": '',
                "runame": '',
                "medal_room_id": 0,
                "mcolor": 0,
                "special_medal": 0,

                "user_level": 0,
                "ulevel_color": 0xffffff,
                "ulevel_rank": ">50000",

                "old_title": "",
                "title": "",

                "privilege_type": v[7],
            }
        return v
