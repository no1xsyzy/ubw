from ._base import *


class PopularRankGuideCardData(BaseModel):
    ruid: int
    title: str
    sub_text: str = "帮我投喂人气票冲榜吧~"
    icon_img: str
    gift_id: int
    countdown: int
    popup_title: str = '投喂一个人气票帮助主播打榜~'


class PopularRankGuideCardCommand(CommandModel):
    cmd: Literal['POPULAR_RANK_GUIDE_CARD']
    data: PopularRankGuideCardData
