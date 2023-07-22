from ._base import *


class Platform(BaseModel):
    android: bool
    ios: bool
    web: bool


class LittleMessageBoxData(BaseModel):
    from_: str = Field(alias='from')
    msg: str
    platform: Platform
    room_id: int
    type: int


class LittleMessageBoxCommand(CommandModel):
    """目前看来只有『今日首条弹幕发送成功~亲密度+100』这个提示"""
    cmd: Literal['LITTLE_MESSAGE_BOX']
    data: LittleMessageBoxData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"{self.data.msg}",
            user=None,
            room_id=self.data.room_id,
            raw=self,
        )
