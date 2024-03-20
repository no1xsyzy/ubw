from ._base import *


class GuardBuyMessage(BaseModel):
    """上舰消息
    :var uid: 用户ID
    :var username: 用户名
    :var guard_level: 舰队等级，0非舰队，1总督，2提督，3舰长
    :var num: 数量
    :var price: 单价金瓜子数
    :var gift_id: 礼物ID
    :var gift_name: 礼物名
    :var start_time: 开始时间戳，和结束时间戳相同
    :var end_time: 结束时间戳，和开始时间戳相同
    """

    uid: int
    username: str
    guard_level: int
    num: int
    price: int
    gift_id: int
    gift_name: str
    start_time: datetime
    end_time: datetime


class GuardBuyCommand(CommandModel):
    cmd: Literal['GUARD_BUY']
    data: GuardBuyMessage

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.start_time,
            msg=f"{self.data.username} 购买了 {self.data.gift_name}x{self.data.num} (￥{self.data.price / 1000})",
            user=(self.data.uid, self.data.username),
            room_id=0,
            price=self.data.price / 1000,
            raw=self,
        )
