from ._base import *


class NoticeMsgCommand(CommandModel):
    cmd: Literal['NOTICE_MSG']
    id: int

    name: str
    msg_type: int
    """1:人气榜第一名
    2:3D小电视飞船专用
    2:大乱斗连胜人气红包"""

    msg_common: str
    msg_self: str

    full: dict
    half: dict
    side: dict = {}

    roomid: int
    real_roomid: int
    link_url: str

    shield_uid: int | None = None
    business_id: str | None = None
    scatter: Scatter | None = None
    marquee_id: str | None = None
    notice_type: int | None = None

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.msg_common.strip() or self.msg_self.strip() or repr(self),
            room_id=self.real_roomid,
            raw=self,
        )
