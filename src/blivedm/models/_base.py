import json
import re
from datetime import datetime, timezone, timedelta
from typing import Annotated, runtime_checkable, Protocol, Union, Literal

from pydantic import BaseModel, Field, root_validator, validator, Field

__all__ = (
    'BaseModel', 'CommandModel', 'datetime', 'timedelta', 'timezone', 'Literal', 'Annotated', 'Union',
    'Summary', 'Summarizer',
    'Scatter', 'strange_dict', 'Color', 'validator', 'Field', 'MedalInfo',
)


class Summary(BaseModel):
    t: datetime
    msg: str | None = None
    user: tuple[int, str] | None = None
    room_id: int | None = None
    price: float = 0
    raw: BaseModel | None = None


@runtime_checkable
class Summarizer(Protocol):
    def summarize(self) -> Summary: ...


class Scatter(BaseModel):
    min: int
    max: int


class CommandModel(BaseModel):
    cmd: str
    ct: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(seconds=8 * 3600))))

    class Config:
        extra = 'forbid'


class Color(BaseModel):
    __root__: Union[str, int]

    @root_validator(pre=True)
    def parse_color(cls, values):
        data = values['__root__']
        if isinstance(data, str) and data.startswith("#"):
            data = data.lstrip("#")
            if len(data) == 3:
                r, g, b = data
                data = r + r + g + g + b + b
        elif isinstance(data, int):
            data = ("000000" + hex(data)[2:])[-6:]
        if re.match("[0-9a-fA-F]{6}", data):
            return {'__root__': data}
        else:
            raise ValueError(f"`{values['__root__']}` is not a valid color")

    @property
    def hashcolor(self):
        return "#" + self.__root__

    @property
    def contrast_black_or_white(self):
        return 'black' if max(self.red, self.green, self.blue) > 127 else 'white'

    @property
    def red(self):
        return int(self.__root__[:2], 16)

    @property
    def green(self):
        return int(self.__root__[2:4], 16)

    @property
    def blue(self):
        return int(self.__root__[4:], 16)

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
    medal_color: Color
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
