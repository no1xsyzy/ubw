from ._base import *


class HorizontalMp4(BaseModel):
    mp4: str
    mp4_md5: str
    mp4_json: str
    mp4_crc32: int
    mp4_file_size: int


class VerticalMp4(BaseModel):
    mp4: str
    mp4_md5: str
    mp4_json: str
    mp4_crc32: int
    mp4_file_size: int


class H265Conf(BaseModel):
    horizontal_mp4: HorizontalMp4
    vertical_mp4: VerticalMp4


class AniRes(BaseModel):
    id: int
    type: int
    weight: int
    web_mp4_json: str
    web_svga: str
    horizontal_svga: str
    vertical_svga: str
    web_mp4: str
    horizontal_mp4: str
    vertical_mp4: str
    horizontal_mp4_md5: str
    vertical_mp4_md5: str
    web_mp4_md5: str
    horizontal_mp4_crc32: int
    vertical_mp4_crc32: int
    web_mp4_crc32: int
    horizontal_mp4_file_size: int
    vertical_mp4_file_size: int
    web_mp4_file_size: int
    h265_conf: H265Conf
    plan_platform: list[int]
    broadcast_scope: int
    bind_giftids: list[int]
    title: str
    online_time: datetime
    offline_time: int
    ctime: datetime
    mtime: datetime


class Data(BaseModel):
    list: list[AniRes]


class LiveAniResUpdateCommand(CommandModel):
    cmd: Literal['LIVE_ANI_RES_UPDATE']
    data: Data
