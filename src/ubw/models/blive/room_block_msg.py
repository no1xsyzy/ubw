from ._base import *


class RoomBlockMsg(BaseModel):
    dmscore: int
    operator: int
    uid: int
    uname: str

    block_expired: datetime | None = None
    vaild_period: str | None = None


class RoomBlockCommand(CommandModel):
    cmd: Literal['ROOM_BLOCK_MSG']
    data: RoomBlockMsg
    uid: str | int
    uname: str

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"用户 {self.data.uname}（uid={self.data.uid}）被封禁",
            user=(self.data.uid, self.data.uname),
            raw=self,
        )
