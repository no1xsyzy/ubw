from ._base import *


class PlatformInfo(BaseModel):
    platform: str
    condition: int
    build: int


class ActivityBannerV2(BaseModel):
    id: int
    position: str
    type: int
    activity_title: str
    cover: str
    jump_url: str
    is_close: int
    action: str
    platform_info: list[PlatformInfo]
    ext_data: str


class ActivityBannerChangeV2Data(BaseModel):
    timestamp: datetime
    list: list[ActivityBannerV2]


class ActivityBannerChangeV2Command(CommandModel):
    cmd: Literal['ACTIVITY_BANNER_CHANGE_V2']
    data: ActivityBannerChangeV2Data
