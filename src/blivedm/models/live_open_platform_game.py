from ._base import *


class InteractivePanelConf(BaseModel):
    dragHeight: int
    dragPosition: tuple[int, int]
    dragWidth: int
    dragable: bool
    general_panel: bool
    iframeHeight: int
    iframeWidth: int
    mode: str
    padding: int
    position: str
    url: str
    zoomPosition: tuple[int, int]
    zoomable: bool
    zoompic: list[str]


class Dm(BaseModel):
    dm_text: str
    dm_key: str
    dm_effect: str


class Gift(BaseModel):
    gift_id: int
    gift_desc: str
    gift_name: str
    gift_icon: str
    gift_price_gold: int
    gift_price_cell: int


class GameMsg(BaseModel):
    play_instructions: str
    dm_command: list[Dm]
    gift_command: list[Gift]


class Data(BaseModel):
    block_uids: list[int]
    game_code: str
    game_conf: str
    game_id: str
    game_msg: GameMsg | dict[None, None]
    game_name: str
    game_status: str
    interactive_panel_conf: InteractivePanelConf | dict[None, None]
    msg_sub_type: str
    msg_type: str
    timestamp: datetime

    validate_game_msg = validator('game_msg', pre=True, allow_reuse=True)(strange_dict)
    validate_interactive_panel_conf = validator('interactive_panel_conf', pre=True, allow_reuse=True)(strange_dict)


class LiveOpenPlatformGameCommand(CommandModel):
    cmd: Literal['LIVE_OPEN_PLATFORM_GAME']
    data: Data
