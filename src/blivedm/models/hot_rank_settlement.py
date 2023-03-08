from ._base import *


class HotRankSettlementData(BaseModel):
    rank: int
    """排名"""
    uname: str
    """主播用户名"""
    face: str
    """主播头像"""
    timestamp: datetime
    """达成时间"""
    icon: str
    """榜单图标"""
    area_name: str
    """榜单名称"""
    url: str
    cache_key: str
    dm_msg: str
    """文字描述"""
    dmscore: int | None = None


class HotRankSettlementV2Command(CommandModel):
    cmd: Literal['HOT_RANK_SETTLEMENT_V2']
    data: HotRankSettlementData

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.timestamp,
            msg=self.data.dm_msg,
            raw=self,
        )


class HotRankSettlementCommand(CommandModel):
    cmd: Literal['HOT_RANK_SETTLEMENT']
    data: HotRankSettlementData

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.timestamp,
            msg=self.data.dm_msg,
            raw=self,
        )
