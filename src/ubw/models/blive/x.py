from ._base import *


class XHeartbeatCommand(CommandModel):
    """构造心跳消息
    :var popularity: 人气值
    :var client_heartbeat_content: 回传心跳消息
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


class XStartCommand(CommandModel):
    """开始侦听房间并传递数据"""
    cmd: Literal['X_UBW_START']


class XStopCommand(CommandModel):
    """结束侦听房间"""
    cmd: Literal['X_UBW_STOP']
