from ._base import *


class VoiceChatUpdateData(BaseModel):
    url: str


class VoiceChatUpdateCommand(CommandModel):
    cmd: Literal['VOICE_CHAT_UPDATE'] = 'VOICE_CHAT_UPDATE'
    data: VoiceChatUpdateData
