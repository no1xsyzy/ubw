from ._base import *


class ActivityBanner(BaseModel):
    id: int
    timestamp: datetime
    position: str
    activity_title: str
    cover: str
    jump_url: str
    is_close: int
    action: str


class ActivityBannerChangeData(BaseModel):
    list: list[ActivityBanner]


class ActivityBannerChangeCommand(CommandModel):
    cmd: Literal['ACTIVITY_BANNER_CHANGE']
    data: ActivityBannerChangeData
