from ._base import *


class WarningCommand(CommandModel):
    """超管警告"""
    cmd: Literal['WARNING']
    msg: str
    roomid: int

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.msg,
            room_id=self.roomid,
            raw=self,
        )
