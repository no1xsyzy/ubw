from ._base import *


class CardData(BaseModel):
    arouse: int
    interval: int
    msg: str
    room_id: int
    source_event: int
    uid: int


class CardMsgData(BaseModel):
    card_data: CardData
    card_type: Literal['daily_recommend']


class CardMsgCommand(CommandModel):
    """
    这是一个特殊的cmd，它依据的是Client登录时的uid而无视room_id，也就是说它可以用于跟踪uid行动
    目前来说唯一已知的触发情况是访问未关注主播间一段时间后弹出的“主播@你……”的提示关注信息
    """
    cmd: Literal['CARD_MSG']
    data: CardMsgData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.data.card_data.msg,
            user=(self.data.card_data.uid, None),
            room_id=self.data.card_data.room_id,
            raw=self,
        )
