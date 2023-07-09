from ._base import *


class MessageboxUserMedalChangeData(BaseModel):
    type: int
    guard_level: int
    is_lighted: int
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    medal_name: str
    multi_unlock_level: str
    MultiUnlockLevel: list
    uid: int
    unlock: int
    unlock_level: int
    up_uid: int
    upper_bound_content: str


class MessageboxUserMedalChangeCommand(CommandModel):
    cmd: Literal['MESSAGEBOX_USER_MEDAL_CHANGE']
    data: MessageboxUserMedalChangeData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.data.upper_bound_content,
            user=(self.data.uid, None),
            raw=self,
        )
