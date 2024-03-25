import json
from datetime import datetime, timezone, timedelta, date
from typing import Annotated, runtime_checkable, Protocol, Union, Literal

from pydantic import BaseModel as _BaseModel, Field, model_validator, field_validator, Field, RootModel, AliasChoices, \
    ConfigDict

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
        elif isinstance(data, tuple):
            if len(data) in [3, 4]:
                return data
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
        return int(self.__root__[6:]) if len(self.__root__) > 6 else None

    def __str__(self):
        return "#" + self.__root__


def strange_dict(cls, v):
    try:
        if not isinstance(v, dict):
            v = json.loads(v)
        if not v:
            return {}
        return v
    except (json.JSONDecodeError, TypeError):
        return {}


def convert_ns(cls, v):
    if isinstance(v, int):
        if v > 2e13 or v < -2e13:
            v = v / 1e6
    return v


class MedalInfo(BaseModel):
    anchor_roomid: int
    """粉丝牌主播房间号"""
    anchor_uname: str
    """粉丝牌主播用户名"""
    guard_level: int
    """大航海等级"""
    icon_id: int
    is_lighted: int
    """点亮？"""
    medal_color: Color | Literal['']
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    """粉丝牌等级"""
    medal_name: str
    """粉丝牌名称"""
    special: str
    target_id: int
    """粉丝牌主播uid"""


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
    face: str
    name_color: Color
    is_mystery: bool
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
    is_guard_leader: bool


class UheadFrame(BaseModel):
    id: int
    frame_img: str


class Uinfo(BaseModel):
    uid: int
    base: UinfoBase
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
