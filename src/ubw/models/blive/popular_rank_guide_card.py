from ._base import *


class PopularRankGuideCardData(BaseModel):
    pass


class PopularRankGuideCardCommand(CommandModel):
    cmd: Literal['POPULAR_RANK_GUIDE_CARD']
    data: PopularRankGuideCardData
