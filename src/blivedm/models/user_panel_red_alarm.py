from ._base import *


class UserPanelRedAlarmData(BaseModel):
    alarm_num: int
    module: str


class UserPanelRedAlarmCommand(CommandModel):
    """可能是直播页面的右上角红点"""
    cmd: Literal['USER_PANEL_RED_ALARM']
    data: UserPanelRedAlarmData
