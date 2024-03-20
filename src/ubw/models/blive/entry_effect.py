from ._base import *


class WealthyInfo(BaseModel):
    uid: int
    level: int
    level_total_score: int
    cur_score: int
    upgrade_need_score: int
    status: int
    dm_icon_key: str


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
    effective_time_new: float
    web_dynamic_url_webp: str
    web_dynamic_url_apng: str
    mobile_dynamic_url_webp: str
    highlight_color: Color
    wealthy_info: WealthyInfo | None = None
    new_style: int
    is_mystery: bool = False
    uinfo: Uinfo

    trigger_time_ns = field_validator('trigger_time', mode='before')(convert_ns)


class EntryEffectCommand(CommandModel):
    cmd: Literal['ENTRY_EFFECT']
    data: EntryEffectData

    def summary(self) -> Summary:
        return Summary(
            t=self.data.trigger_time,
            msg=self.data.copy_writing,
            user=(self.data.uid, None),
            room_id=self.data.target_id,
            raw=self,
        )


class EntryEffectMustReceiveCommand(CommandModel):
    cmd: Literal['ENTRY_EFFECT_MUST_RECEIVE']
    data: EntryEffectData

    def summary(self) -> Summary:
        return Summary(
            t=self.data.trigger_time,
            msg=self.data.copy_writing,
            user=(self.data.uid, None),
            room_id=self.data.target_id,
            raw=self,
        )
