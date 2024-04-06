from ._base import *


class XHeartbeatCommand(CommandModel):
    """构造心跳消息
    :var popularity: 人气值
    """
    cmd: Literal['X_UBW_HEARTBEAT']
    popularity: int
    client_heartbeat_content: str

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"人气值：{self.popularity}",
            room_id=None,
            raw=self,
        )
