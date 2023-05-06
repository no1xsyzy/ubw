from ._base import *


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


class InitInfo(BaseModel):
    date_streak: int
    room_id: int


class MatchInfo(BaseModel):
    date_streak: int
    room_id: int


class PkBattleStartData(BaseModel):
    battle_type: int
    final_conf: FinalConfData
    final_hit_votes: int
    init_info: InitInfo
    match_info: MatchInfo
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


class AssistInfo(BaseModel):
    face: str
    rank: int
    uid: int
    uname: str


class PkBattleProcessNewInfo(BaseModel):
    assist_info: list[AssistInfo] | None
    best_uname: str
    room_id: int
    votes: int


class PkBattleProcessNewData(BaseModel):
    battle_type: int
    init_info: PkBattleProcessNewInfo
    match_info: PkBattleProcessNewInfo


class PkBattleProcessNewCommand(CommandModel):
    cmd: Literal['PK_BATTLE_PROCESS_NEW']
    pk_id: int
    pk_status: int
    data: PkBattleProcessNewData
    timestamp: datetime


class DmConf(BaseModel):
    bg_color: Color
    font_color: Color


class PkBattleSettleNewInfo(BaseModel):
    assist_info: list[AssistInfo]
    result_type: int
    room_id: int
    votes: int


class PkBattleSettleNewData(BaseModel):
    battle_type: int
    dm_conf: DmConf
    dmscore: int
    init_info: PkBattleSettleNewInfo
    match_info: PkBattleSettleNewInfo
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
