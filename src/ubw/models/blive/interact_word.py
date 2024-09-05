from typing import ClassVar

from ._base import *


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


class ContributionV2(BaseModel):
    grade: int
    rank_type: str
    text: str


class RelationTail(BaseModel):
    tail_guide_text: str
    tail_icon: str
    tail_type: int


class InteractWordData(BaseModel):
    contribution: Contribution | None = None
    contribution_v2: ContributionV2 | None = None
    core_user_type: int
    dmscore: int | None = None
    fans_medal: FansMedal | None
    identities: list[int] | None
    is_spread: int
    msg_type: int
    """1=进入，2=关注，3=分享，4=特别关注，5=互相关注"""
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
    roomid: int
    group_medal: GroupMedal | None = None
    is_mystery: bool = False
    tail_text: str = ''
    uinfo: Uinfo | None = None

    relation_tail: RelationTail | None = None

    trigger_time_ns = field_validator('trigger_time', mode='before')(convert_ns)


class InteractWordCommand(CommandModel):
    cmd: Literal['INTERACT_WORD']
    data: InteractWordData

    MSG_NAME: ClassVar = {
        1: '进入',
        2: '关注',
        3: '分享',
        4: '特别关注',
        5: '互相关注',
    }

    def summarize(self):
        if self.data.msg_type in self.MSG_NAME:
            msg = f"{self.data.uname} {self.MSG_NAME[self.data.msg_type]}了 {self.data.roomid}"
        else:
            msg = f"{self.data.uname}/{self.data.roomid} (msg_type={self.data.msg_type})"

        return Summary(
            t=self.data.timestamp,
            msg=msg,
            user=(self.data.uid, self.data.uname),
            raw=self,
        )
