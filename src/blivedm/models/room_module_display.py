from ._base import *


class Modules(BaseModel):
    bottom_banner: int
    top_banner: int
    widget_banner: int


class Data(BaseModel):
    modules: Modules
    timestamp: int


class RoomModuleDisplayCommand(CommandModel):
    cmd: Literal['ROOM_MODULE_DISPLAY']
    data: Data
