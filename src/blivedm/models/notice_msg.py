from ._base import *


class FullNotice(BaseModel):
    background: str
    color: str
    highlight: str

    head_icon: str
    head_icon_fa: str
    head_icon_fan: int

    tail_icon: str
    tail_icon_fa: str
    tail_icon_fan: int

    time: int


class HalfNotice(BaseModel):
    background: str
    color: str
    highlight: str

    head_icon: str
    tail_icon: str

    time: int


class SideNotice(BaseModel):
    background: str
    border: str
    color: str
    highlight: str

    head_icon: str


class NoticeMsgCommandBase(CommandModel):
    cmd: Literal['NOTICE_MSG']
    msg_type: int


class NoticeMsgCommand1(NoticeMsgCommandBase):
    msg_type: Literal[1]

    msg_common: str
    msg_self: str
    roomid: int
    real_roomid: int
    notice_type: int
    shield_uid: int
    id: int
    name: str
    business_id: str
    marquee_id: Literal['']
    link_url: str

    full: FullNotice
    half: HalfNotice
    side: SideNotice

    scatter: Scatter


class NoticeMsgCommand2(NoticeMsgCommandBase):
    msg_type: Literal[2]

    msg_common: str
    msg_self: str
    roomid: int
    real_roomid: int
    notice_type: int
    shield_uid: int
    id: int
    name: str
    business_id: str
    marquee_id: Literal['']
    link_url: str

    side: SideNotice
    full: FullNotice
    half: HalfNotice

    scatter: Scatter


class NoticeMsgCommand3(NoticeMsgCommandBase):
    msg_type: Literal[3]

    msg_common: str
    msg_self: str
    roomid: int
    real_roomid: int
    id: int
    name: str
    link_url: str
    business_id: str
    marquee_id: Literal['']
    notice_type: int
    shield_uid: int

    side: SideNotice
    full: FullNotice
    half: HalfNotice

    scatter: Scatter


class NoticeMsgCommand4(NoticeMsgCommandBase):
    msg_type: Literal[4]

    msg_common: str
    msg_self: str
    roomid: int
    real_roomid: int
    id: int
    name: str
    link_url: str
    business_id: str
    marquee_id: Literal['']
    notice_type: int
    shield_uid: int

    side: SideNotice
    full: FullNotice
    half: HalfNotice

    scatter: Scatter


class NoticeMsgCommand6(NoticeMsgCommandBase):
    msg_type: Literal[6]

    msg_common: str
    msg_self: str

    roomid: int
    real_roomid: int
    link_url: str

    full: FullNotice
    half: HalfNotice

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.msg_common.strip() or self.msg_self.strip() or repr(self),
            room_id=self.real_roomid,
            raw=self,
        )


class NoticeMsgCommand9(NoticeMsgCommandBase):
    msg_type: Literal[9]

    msg_common: str
    msg_self: str

    link_url: str
    roomid: int
    real_roomid: int
    shield_uid: str  # 其他一直保持 -1，唯独 msg_type=9 与众不同？

    full: FullNotice
    half: HalfNotice
    side: SideNotice


NoticeMsgCommand = Annotated[Union[
    NoticeMsgCommand1,
    NoticeMsgCommand2,
    NoticeMsgCommand3,
    NoticeMsgCommand4,
    NoticeMsgCommand6,
    NoticeMsgCommand9,
], Field(discriminator='msg_type')]
