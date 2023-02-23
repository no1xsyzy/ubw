from datetime import datetime, timezone, timedelta
from typing import *

from pydantic import BaseModel, validator, Field
from pydantic.generics import GenericModel

DataV = TypeVar('DataV')


class Response(GenericModel, Generic[DataV]):
    code: int
    message: str
    ttl: int
    data: DataV | None


class BaseInfo(BaseModel):
    uname: str
    face: str
    gender: str


class AnchorInfo(BaseModel):
    base_info: BaseInfo

class RoomInfo(BaseModel):
    room_id: int
    short_id: int
    uid: int
    live_start_time: datetime | None
    title: str
    cover: str
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    keyframe: str
    """关键帧URL"""

    @validator('live_start_time', pre=True)
    def live_start_time_zero_means_none(cls, v):
        if v == 0:
            return None
        return v


class InfoByRoom(BaseModel):
    room_info: RoomInfo
    ct: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(seconds=8 * 3600))))


class Host(BaseModel):
    host: str
    port: int
    wss_port: int
    ws_port: int


class DanmuInfo(BaseModel):
    group: str
    business_id: int
    refresh_row_factor: float
    refresh_rate: int
    max_delay: int
    token: str
    host_list: list[Host]
