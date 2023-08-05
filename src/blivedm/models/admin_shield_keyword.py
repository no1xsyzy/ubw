from ._base import *


class Data(BaseModel):
    action: int
    keyword: str
    name: str
    uid: int


class AdminShieldKeywordCommand(CommandModel):
    cmd: Literal['ADMIN_SHIELD_KEYWORD']
    data: Data
