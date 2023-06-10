from ._base import *


class AssistInfo(BaseModel):
    face: str
    rank: int
    uid: int
    uname: str


class PkInfo(BaseModel):
    room_id: int
    date_streak: int | None = None
    vision_desc: int | None = None
    best_uname: str | None = None
    votes: int | None = None
    assist_info: list[AssistInfo] | None = None
    result_type: int | None = None
    winner_type: int | None = None


class PkBattleRankChangeData(BaseModel):
    first_rank_img_url: str
    rank_name: str


class PkBattleRankChangeCommand(CommandModel):
    cmd: Literal['PK_BATTLE_RANK_CHANGE']
    data: PkBattleRankChangeData
    timestamp: datetime


class PkBattlePreData(BaseModel):
    battle_type: int
    end_win_task: None
    is_followed: bool = False
    face: str
    match_type: int
    pk_votes_name: str
    pre_timer: int
    room_id: int
    season_id: int
    uid: int
    uname: str


class PkBattlePreCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PRE']
    pk_id: int
    pk_status: int
    roomid: int
    data: PkBattlePreData
    timestamp: datetime


class PkBattlePreNewCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PRE_NEW']
    pk_id: int
    pk_status: int
    roomid: int = 0
    status_msg: str = ""
    data: PkBattlePreData
    timestamp: datetime


class FinalConfData(BaseModel):
    end_time: datetime
    start_time: datetime
    switch: int


class PkBattleStartData(BaseModel):
    battle_type: int
    final_conf: FinalConfData
    final_hit_votes: int
    init_info: PkInfo
    match_info: PkInfo
    pk_countdown: datetime
    pk_end_time: datetime
    pk_frozen_time: datetime
    pk_start_time: datetime
    pk_votes_add: int
    pk_votes_name: str
    pk_votes_type: int
    star_light_msg: str


class PkBattleStartCommand(CommandModel):
    cmd: Literal['PK_BATTLE_START']
    pk_id: int
    pk_status: int
    roomid: int
    data: PkBattleStartData
    timestamp: datetime


class PkBattleStartNewCommand(CommandModel):
    cmd: Literal['PK_BATTLE_START_NEW']
    pk_id: int
    pk_status: int
    roomid: int
    data: PkBattleStartData
    timestamp: datetime


class PkBattlePunishEndData(BaseModel):
    battle_type: int


class PkBattlePunishEndCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PUNISH_END']
    pk_id: int
    pk_status: int
    status_msg: str
    data: PkBattlePunishEndData
    timestamp: datetime


class PkBattleProcessData(BaseModel):
    battle_type: int
    init_info: PkInfo
    match_info: PkInfo


class PkBattleProcessCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PROCESS']
    pk_id: int
    pk_status: int
    data: PkBattleProcessData
    timestamp: datetime


class PkBattleProcessNewCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PROCESS_NEW']
    pk_id: int
    pk_status: int
    data: PkBattleProcessData
    timestamp: datetime


class DmConf(BaseModel):
    bg_color: Color
    font_color: Color


class PkBattleSettleNewData(BaseModel):
    battle_type: int
    dm_conf: DmConf
    dmscore: int
    init_info: PkInfo
    match_info: PkInfo
    pk_id: int
    pk_status: int
    punish_end_time: datetime
    settle_status: int
    timestamp: datetime


class PkBattleSettleNewCommand(CommandModel):
    cmd: Literal['PK_BATTLE_SETTLE_NEW']
    pk_id: int
    pk_status: int
    data: PkBattleSettleNewData
    timestamp: datetime


class LevelInfo(BaseModel):
    first_rank_img: str
    first_rank_name: str
    second_rank_icon: str
    second_rank_num: int
    uid: int | None = None


class ResultInfo(BaseModel):
    pk_extra_value: int
    pk_votes: int
    pk_votes_name: str
    total_score: int


class PkBattleSettleV2Command(CommandModel):
    cmd: Literal['PK_BATTLE_SETTLE_V2']
    pk_id: int
    pk_status: int
    settle_status: int
    timestamp: datetime
    data: dict  # 太复杂、一直在变、只是为了爆米，谁爱写解析谁写


class PkBattleEndData(BaseModel):
    battle_type: int
    init_info: PkInfo
    match_info: PkInfo


class PkBattleEndCommand(CommandModel):
    cmd: Literal['PK_BATTLE_END']
    pk_id: int
    pk_status: int
    data: PkBattleEndData
    timestamp: datetime


class PkBattleFinalProcessData(BaseModel):
    battle_type: int
    pk_frozen_time: datetime


class PkBattleFinalProcessCommand(CommandModel):
    cmd: Literal['PK_BATTLE_FINAL_PROCESS']
    pk_id: int
    pk_status: int
    data: PkBattleFinalProcessData
    timestamp: datetime


class PkBattleEntranceData(BaseModel):
    is_open: bool


class PkBattleEntranceCommand(CommandModel):
    cmd: Literal['PK_BATTLE_ENTRANCE']
    data: PkBattleEntranceData
    timestamp: datetime


class PkBattleSettleData(BaseModel):
    battle_type: int
    result_type: int
    star_light_msg: str


class PkBattleSettleCommand(CommandModel):
    cmd: Literal['PK_BATTLE_SETTLE']
    pk_id: int
    pk_status: int
    settle_status: int
    timestamp: datetime
    data: PkBattleSettleData
    roomid: int


class PkBattleSettleUserCommand(CommandModel):
    cmd: Literal['PK_BATTLE_SETTLE_USER']
    pk_id: int
    pk_status: int
    settle_status: int
    timestamp: datetime
    data: dict  # 太复杂而且只是为了爆米，谁爱写解析谁写
