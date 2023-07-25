from ._base import *


class Data(BaseModel):
    area_id: int
    has_perm: int
    show_count: int


class PlaytogetherIconChangeCommand(CommandModel):
    cmd: Literal['PLAYTOGETHER_ICON_CHANGE']
    data: Data
