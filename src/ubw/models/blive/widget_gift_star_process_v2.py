from ._base import *


class WidgetGiftStarProcessV2Data(BaseModel):
    name: str
    cur_num: int
    total_num: int
    version: int


class WidgetGiftStarProcessV2Command(CommandModel):
    cmd: Literal['WIDGET_GIFT_STAR_PROCESS_V2']
    data: WidgetGiftStarProcessV2Data
