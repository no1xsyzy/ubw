from ._base import *


class LevelInfo(BaseModel):
    star_name: str
    level_tip: str
    level_img: str
    level_id: int


class WidgetGiftStarProcess(BaseModel):
    gift_id: int
    gift_img: str
    gift_name: str
    completed_num: int
    target_num: int


class WidgetGiftStarProcessData(BaseModel):
    start_date: date
    process_list: list[WidgetGiftStarProcess]
    finished: bool
    ddl_timestamp: datetime
    version: datetime
    reward_gift: int
    reward_gift_img: str
    reward_gift_name: str

    level_info: LevelInfo | None = None

    @field_validator('start_date', mode='before')
    @classmethod
    def start_date_is_yyyymmdd_int(cls, v):
        if isinstance(v, int):
            return date(v // 10000, v // 100 % 100, v % 100)
        return v


class WidgetGiftStarProcessCommand(CommandModel):
    cmd: Literal['WIDGET_GIFT_STAR_PROCESS']
    data: WidgetGiftStarProcessData
