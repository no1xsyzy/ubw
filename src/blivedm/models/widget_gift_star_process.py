from ._base import *


class WidgetGiftStarProcess(BaseModel):
    gift_id: int
    gift_img: str
    gift_name: str
    completed_num: str
    target_num: str


class WidgetGiftStarProcessData(BaseModel):
    start_date: str
    process_list: list[WidgetGiftStarProcess]
    finished: bool
    ddl_timestamp: datetime
    version: datetime
    reward_gift: int
    reward_gift_img: str
    reward_gift_name: str


class WidgetGiftStarProcessCommand(CommandModel):
    cmd: Literal['WIDGET_GIFT_STAR_PROCESS']
    data: WidgetGiftStarProcessData
