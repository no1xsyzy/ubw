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
    roomid: int
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
