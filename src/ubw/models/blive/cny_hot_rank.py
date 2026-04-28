from ._base import *


class InviteFriendIcon(BaseModel):
    icon: str
    text: str


class CnyHotRankData(BaseModel):
    face: str
    name: str
    room_id: int
    title: str
    subtitle: str
    report_type: int
    invite_friend_icon: InviteFriendIcon


class CnyHotRankCommand(CommandModel):
    """春节热度排行"""
    cmd: Literal['CNY_HOT_RANK']
    data: CnyHotRankData
