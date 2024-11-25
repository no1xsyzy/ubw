from ._base import *


class Data(BaseModel):
    """删除醒目留言消息"""
    ids: list[int]
    """醒目留言ID数组"""


class SuperChatMessageDeleteCommand(CommandModel):
    cmd: Literal['SUPER_CHAT_MESSAGE_DELETE']
    data: Data
    roomid: int
