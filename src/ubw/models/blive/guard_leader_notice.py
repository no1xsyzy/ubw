from ._base import *


class Data(BaseModel):
    display_src: str
    uid: int
    rank_top_icon1: str
    rank_top_background_url1: str
    rank_top_background_url2: str
    svga_Block: int
    input_background_url: str
    rank_top_icon2: str
    rank_top_background_light_url2: str
    anchor_effect_id: int
    effect_id: int
    avatar_src: str
    name: str
    face: str
    jump_url: str
    anchor_background_url: str
    background_url: str
    show: int


class GuardLeaderNoticeCommand(CommandModel):
    cmd: Literal['GUARD_LEADER_NOTICE']
    data: Data
