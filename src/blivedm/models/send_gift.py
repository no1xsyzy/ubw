from ._base import *


class GiftMessage(BaseModel):
    """礼物消息"""
    giftName: str
    """礼物名"""
    num: int
    """数量"""
    uname: str
    """用户名"""
    face: str
    """用户头像URL"""
    guard_level: int
    """舰队等级，0非舰队，1总督，2提督，3舰长"""
    uid: int
    """用户ID"""
    timestamp: datetime
    """时间戳"""
    giftId: int
    """礼物ID"""
    giftType: int
    """礼物类型（未知）"""
    action: str
    """目前遇到的有'喂食'、'赠送'"""
    price: int
    """礼物单价瓜子数"""
    rnd: str
    """随机数，可能是去重用的。有时是时间戳+去重ID，有时是UUID"""
    coin_type: str
    """瓜子类型，'silver'或'gold'，1000金瓜子 = 1元"""
    total_coin: int
    """总瓜子数"""
    tid: str
    """可能是事务ID，有时和rnd相同"""


class GiftCommand(CommandModel):
    cmd: Literal['SEND_GIFT']
    data: GiftMessage

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.timestamp,
            msg=f"{self.data.action} {self.data.giftName}x{self.data.num}",
            user=(self.data.uid, self.data.uname),
            price=self.data.price if self.data.coin_type == 'gold' else 0,
            raw=self,
        )
