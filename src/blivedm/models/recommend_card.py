from ._base import *


class VirtualExtraInfo(BaseModel):
    goods_type: int
    web_container_type: int


class PriceInf(BaseModel):
    prefix_price: str
    sale_price: str
    suffix_price: str
    strock_price: str
    sale_start_time: datetime
    sale_end_time: datetime
    strock_show: int


class PriceInfo(BaseModel):
    normal: PriceInf | None
    activity: PriceInf | None


class BtnInfo(BaseModel):
    card_btn_status: int
    card_btn_title: str
    card_btn_style: int
    card_btn_jumpurl: str


class RecommendCardData(BaseModel):
    title_icon: str
    recommend_list: list[dict]  # 太复杂、一直在变、只是为了收米，谁爱写解析谁写
    timestamp: datetime


class RecommendCardCommand(CommandModel):
    cmd: Literal['RECOMMEND_CARD']
    data: RecommendCardData
