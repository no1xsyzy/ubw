from ._base import *


class Data(BaseModel):
    click: int
    coin_cost: int
    coin_num: int
    cover_btn: str
    cover_url: str
    live_key: str
    order_id: int
    order_type: int
    plan_percent: int
    show: int
    status: int
    timestamp: datetime
    title: str
    total_online: int
    uid: int


class SpreadShowFeetV2Command(CommandModel):
    cmd: Literal['SPREAD_SHOW_FEET_V2']
    data: Data

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"{self.data.uid}使用的{self.data.title} ({self.data.order_type})",
            user=(self.data.uid, None),
            raw=self,
        )
