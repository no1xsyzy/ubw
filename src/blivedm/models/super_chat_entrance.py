from ._base import *


class SuperChatEntranceData(BaseModel):
    broadcast_type: int
    icon: str
    jump_url: str
    status: int


class SuperChatEntranceCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_ENTRANCE']
    data: SuperChatEntranceData
    roomid: int
