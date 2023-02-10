from datetime import datetime
from typing import *

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

DataV = TypeVar('DataV')


class Response(GenericModel, Generic[DataV]):
    code: int
    message: str
    ttl: int
    data: DataV | None


class RoomInfo(BaseModel):
    room_id: int
    short_id: int
    uid: int
    live_start_time: datetime | None

    @validator('live_start_time', pre=True)
    def live_start_time_zero_means_none(cls, v):
        if v == 0:
            return None
        return v


class InfoByRoom(BaseModel):
    room_info: RoomInfo


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
