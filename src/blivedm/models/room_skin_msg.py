from ._base import *


class ZipSkin(BaseModel):
    zip: str
    md5: str


class WebSkin(BaseModel):
    zip: str
    md5: str
    platform: str
    version: str
    headInfoBgPic: str
    giftControlBgPic: str
    rankListBgPic: str
    mainText: str
    normalText: str
    highlightContent: str
    border: str
    buttonText: str | None = None


class SkinConfig(BaseModel):
    android: dict[str, ZipSkin]
    ios: dict[str, ZipSkin]
    ipad: dict[str, ZipSkin]
    web: dict[str, WebSkin]


class RoomSkinCommand(CommandModel):
    cmd: Literal['ROOM_SKIN_MSG']
    skin_id: int
    status: int
    end_time: datetime
    current_time: datetime
    only_local: bool
    skin_config: SkinConfig
    scatter: Scatter
