from datetime import datetime, timezone, timedelta, date
from typing import Annotated, runtime_checkable, Protocol, Union, Literal

from pydantic import BaseModel as _BaseModel, Field, model_validator, field_validator, Field, RootModel, AliasChoices, \
    ConfigDict

from .._base import *

__all__ = (
    # pydantic
    'BaseModel', 'CommandModel', 'model_validator', 'field_validator', 'Field', 'AliasChoices',
    # stdlib
    'datetime', 'timedelta', 'timezone', 'date', 'Literal', 'Annotated', 'Union',
    # interface
    'Summary', 'Summarizer',
    # common types
    'Scatter', 'MedalInfo', 'Color', 'Uinfo', 'UinfoLow', 'UserInfo', 'GroupMedal',
    # common validator
    'strange_dict', 'convert_ns',
)


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid')


class Scatter(BaseModel):
    min: int
    max: int


class CommandModel(BaseModel):
    cmd: str
    ct: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(seconds=8 * 3600))))

    is_report: bool | None = None
    msg_id: str | None = None
    send_time: datetime | None = None
    p_is_ack: bool | None = None
    p_msg_type: int | None = None


class Color(RootModel):
    root: tuple[int, int, int] | tuple[int, int, int, int]

    @model_validator(mode='before')
    def parse_color(cls, data):
        if isinstance(data, str):
            s = data.lstrip("#")
            if len(s) == 3:
                r, g, b = s
                return int(r, 16) * 17, int(g, 16) * 17, int(b, 16) * 17
            elif len(s) == 6:
                r = s[:2]
                g = s[2:4]
                b = s[4:6]
                return int(r, 16), int(g, 16), int(b, 16)
            elif len(s) == 8:
                r = s[:2]
                g = s[2:4]
                b = s[4:6]
                a = s[6:8]
                return int(r, 16), int(g, 16), int(b, 16), int(a, 16)
        elif isinstance(data, int):
            if 0 <= data < 2 ** 24:
                return data // 65536, data // 256 % 256, data % 256
        elif isinstance(data, (tuple, list)):
            if len(data) in [3, 4]:
                return tuple(data)
        raise ValueError(f"`{data!r}` is not a color")

    @property
    def hashcolor(self):
        return "#" + ''.join(hex(p)[2:] for p in self.root)

    @property
    def red(self) -> int:
        return self.root[0]

    @property
    def green(self) -> int:
        return self.root[1]

    @property
    def blue(self) -> int:
        return self.root[2]

    @property
    def alpha(self) -> int | None:
        return int(self.root[3]) if len(self.root) > 3 else None


def convert_ns(cls, v):
    if isinstance(v, int):
        if v > 2e13 or v < -2e13:
            v = v / 1e9
    return v


class MedalInfo(BaseModel):
    """粉丝牌信息
    :var medal_level: 粉丝牌等级
    :var medal_name: 粉丝牌名称
    :var anchor_uname: 粉丝牌主播用户名
    :var anchor_roomid: 粉丝牌主播房间号
    :var medal_color: 粉丝牌颜色
    :var special:
    :var icon_id:
    :var medal_color_border: 更多关于粉丝牌颜色的信息
    :var medal_color_start: 更多关于粉丝牌颜色的信息
    :var medal_color_end: 更多关于粉丝牌颜色的信息
    :var guard_level: 大航海等级
    :var is_lighted: 点亮？
    :var target_id: 粉丝牌主播uid
    """
    medal_level: int
    medal_name: str
    anchor_uname: str
    anchor_roomid: int
    medal_color: Color | Literal['']
    special: str
    icon_id: int
    medal_color_border: Color
    medal_color_start: Color
    medal_color_end: Color
    guard_level: int
    is_lighted: int
    target_id: int


class RiskCtrlInfo(BaseModel):
    name: str
    face: str


class OriginInfo(BaseModel):
    name: str
    face: str


class OfficialInfo(BaseModel):
    role: int
    title: str
    desc: str
    type: int


class UinfoBase(BaseModel):
    name: str
    name_color: Color
    face: str = ''
    is_mystery: bool = False
    risk_ctrl_info: RiskCtrlInfo | None = None
    origin_info: OriginInfo | None = None
    official_info: OfficialInfo | None = None
    name_color_str: str | None = None


class GuardInfo(BaseModel):
    level: int
    expired_str: str


class UinfoMedal(BaseModel):
    color: Color
    color_border: Color
    color_end: Color
    color_start: Color
    guard_icon: str = ''
    guard_level: int = 0
    honor_icon: str = ''
    id: int
    is_light: int
    level: int
    name: str
    ruid: int
    score: int
    typ: int


class UinfoWealth(BaseModel):
    level: int
    dm_icon_key: str


class UinfoTitle(BaseModel):
    old_title_css_id: str
    title_css_id: str


class UinfoGuardLeader(BaseModel):
    is_guard_leader: bool = False


class UheadFrame(BaseModel):
    id: int
    frame_img: str


class Uinfo(BaseModel):
    uid: int
    base: UinfoBase | None = None
    medal: UinfoMedal | None = None
    wealth: UinfoWealth | None = None
    title: UinfoTitle | None = None
    guard: GuardInfo | None = None
    uhead_frame: UheadFrame | None = None
    guard_leader: UinfoGuardLeader | None = None


class UinfoLowBase(BaseModel):
    uname: str
    face: str
    is_mystery: bool


class UinfoLow(BaseModel):
    base: UinfoLowBase


class Summary(BaseModel):
    t: datetime
    msg: str | None = None
    user: tuple[int, str] | tuple[int, None] | tuple[None, str] | None = None
    room_id: int | None = None
    price: float = 0
    raw: CommandModel | None = None


@runtime_checkable
class Summarizer(Protocol):
    def summarize(self) -> Summary: ...


class UserInfo(BaseModel):
    uid: int
    uname: str


class GroupMedal(BaseModel):
    is_lighted: int
    medal_id: int = 0
    name: str = ''
