from ._base import *


class GiftScene(BaseModel):
    scene: str
    pay_type: str


class Animation(BaseModel):
    animation_name: str
    loop: bool
    track_index: int


class ModFilePath(BaseModel):
    mod_name: str
    path: str


class Attachment(BaseModel):
    file_path: ModFilePath
    slot_name: str
    texture: list[str]


class SpineConfig(BaseModel):
    spine_end: str


class Origin(BaseModel):
    x: float
    y: float


class Size(BaseModel):
    height: float
    width: float


class ViewPort(BaseModel):
    origin: Origin | None
    size: Size | None


class SpineInfo(BaseModel):
    animations: list[Animation]
    atlas: str
    attachments: list[Attachment]
    file_path: ModFilePath
    pool_name: str
    spine: str
    spine_config: SpineConfig
    sprite: str
    viewport: ViewPort


class AttireInfo(BaseModel):
    bg_spine_info: SpineInfo
    main_spine_info: SpineInfo


class BizExtra(BaseModel):
    button_combo_type: int
    effect_id: int
    gift_id: int
    attire_info: AttireInfo


class Data(BaseModel):
    uid: int
    effect_id: int
    demarcation: int
    order_id: str

    gift_scene: GiftScene | None = None
    biz_extra: Json[BizExtra] | None = None


class CommonAnimationCommand(CommandModel):
    cmd: Literal['COMMON_ANIMATION']
    data: Data
