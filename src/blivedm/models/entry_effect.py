from ._base import *


class EntryEffectData(BaseModel):
    id: int
    uid: int
    target_id: int
    mock_effect: int
    face: str
    privilege_type: int
    copy_writing: str
    copy_color: Color
    priority: int
    basemap_url: str
    show_avatar: int
    effective_time: int
    web_basemap_url: str
    web_effective_time: int
    web_effect_close: int
    web_close_time: int
    business: int
    copy_writing_v2: str
    icon_list: list
    max_delay_time: int
    trigger_time: datetime
    identities: int
    effect_silent_time: int
    effective_time_new: int
    web_dynamic_url_webp: str
    web_dynamic_url_apng: str
    mobile_dynamic_url_webp: str


class EntryEffectCommand(CommandModel):
    cmd: Literal['ENTRY_EFFECT']
    data: EntryEffectData
