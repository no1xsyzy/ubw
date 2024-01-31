from ._base import *


class PreparingCommand(CommandModel):
    """下播"""
    cmd: Literal['PREPARING']
    roomid: int
    scatter: Scatter | None = None
    round: bool = False

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"下播了",
            room_id=self.roomid,
            raw=self,
        )
