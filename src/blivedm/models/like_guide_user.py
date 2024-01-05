from ._base import *


class Data(BaseModel):
    show_area: int
    like_text: str
    uid: int
    dmscore: int
    identities: list[int]
    msg_type: int


class LikeGuideUserCommand(CommandModel):
    cmd: Literal['LIKE_GUIDE_USER']
    data: Data
