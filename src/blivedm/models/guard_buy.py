from ._base import *


class GuardBuyMessage(BaseModel):
    """上舰消息"""
    uid: int
    """用户ID"""
    username: str
    """用户名"""
    guard_level: int
    """舰队等级，0非舰队，1总督，2提督，3舰长"""
    num: int
    """数量"""
    price: int
    """单价金瓜子数"""
    gift_id: int
    """礼物ID"""
    gift_name: str
    """礼物名"""
    start_time: datetime
    """开始时间戳，和结束时间戳相同"""
    end_time: datetime
    """结束时间戳，和开始时间戳相同"""


class GuardBuyCommand(CommandModel):
    cmd: Literal['GUARD_BUY']
    data: GuardBuyMessage

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.start_time,
            msg=f"{self.data.username} 购买了 {self.data.gift_name}x{self.data.num} (￥{self.data.price})",
            user=(self.data.uid, self.data.username),
            room_id=0,
            price=self.data.price,
            raw=self,
        )
