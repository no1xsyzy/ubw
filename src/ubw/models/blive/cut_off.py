from ._base import *


class CutOffCommand(CommandModel):
    cmd: Literal['CUT_OFF']
    msg: str
    room_id: int = Field(validation_alias=AliasChoices('roomid', 'room_id'))
