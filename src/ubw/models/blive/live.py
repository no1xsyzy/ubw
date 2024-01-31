from ._base import *


class LiveCommand(CommandModel):
    """开播"""
    cmd: Literal['LIVE']
    live_key: str
    voice_background: str
    sub_session_key: str
    live_platform: str
    live_model: int
    live_time: datetime | None = None
    roomid: int

    def summarize(self) -> Summary:
        return Summary(
            t=self.live_time or self.ct,
            msg=f"开播了",
            user=None,
            room_id=self.roomid,
            raw=self,
        )
