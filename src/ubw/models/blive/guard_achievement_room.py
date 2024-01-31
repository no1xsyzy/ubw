from ._base import *


class AnchorModal(BaseModel):
    first_line_content: str
    highlight_color: Color
    second_line_content: str
    show_time: int


class Data(BaseModel):
    anchor_basemap_url: str
    anchor_guard_achieve_level: int
    anchor_modal: AnchorModal
    app_basemap_url: str
    current_achievement_level: int
    """可能1=百舰"""
    dmscore: int
    event_type: int
    face: str
    first_line_content: str
    first_line_highlight_color: str
    first_line_normal_color: str
    headmap_url: str
    is_first: bool
    is_first_new: bool
    room_id: int
    second_line_content: str
    second_line_highlight_color: str
    second_line_normal_color: str
    show_time: int
    web_basemap_url: str


class GuardAchievementRoomCommand(CommandModel):
    cmd: Literal['GUARD_ACHIEVEMENT_ROOM']
    data: Data

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"{self.data.first_line_content}{self.data.second_line_content} "
                f"(level={self.data.current_achievement_level})",
            room_id=self.data.room_id,
            raw=self,
        )
