from ._base import *


class HeartbeatMessage(BaseModel):
    """心跳消息"""

    popularity: int
    """人气值"""


class HeartbeatCommand(CommandModel):
    cmd: Literal['_HEARTBEAT']
    data: HeartbeatMessage
