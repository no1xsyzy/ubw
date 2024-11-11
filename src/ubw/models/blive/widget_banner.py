from ._base import *


class Widget(BaseModel):
    band_id: int
    cover: str
    id: int
    is_add: bool
    jump_url: str
    platform_in: list[str]
    site: int
    stay_time: int
    sub_data: str
    sub_key: str
    tip_bottom_color: Color | Literal[''] = ''
    tip_text: str
    tip_text_color: Color | Literal[''] = ''
    title: str
    type: int
    url: str
    web_cover: str

    position: int | None = None

    target_url: str = ""
    url_type: int = 0
    android_jumpurl: str = ""
    ios_jumpurl: str = ""
    android_schameurl: str = ""
    ios_schemaurl: str = ""


class Data(BaseModel):
    timestamp: datetime
    widget_list: dict[str, Widget | None]


class WidgetBannerCommand(CommandModel):
    cmd: Literal['WIDGET_BANNER']
    data: Data
