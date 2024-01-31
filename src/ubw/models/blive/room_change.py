from ._base import *


class RoomChangeMessage(BaseModel):
    """直播间信息修改"""
    title: str
    area_id: int
    parent_area_id: int
    area_name: str
    parent_area_name: str
    live_key: str
    sub_session_key: str


class RoomChangeCommand(CommandModel):
    cmd: Literal['ROOM_CHANGE']
    data: RoomChangeMessage

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"直播间信息变更《{self.data.title}》，分区：{self.data.parent_area_name}/{self.data.area_name}",
            user=None,
            raw=self,
        )
