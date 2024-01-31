from ._base import *


class MessageboxUserMedalChangeData(BaseModel):
    type: int
    "1=粉丝勋章升级，2=再次点亮"
    guard_level: int
    is_lighted: int
    medal_color_border: Color
    medal_color_end: Color
    medal_color_start: Color
    medal_level: int
    medal_name: str
    multi_unlock_level: str
    MultiUnlockLevel: list[int] = Field(default_factory=list)
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
            msg=self.data.upper_bound_content or (
                f"{self.data.uid}再次点亮了粉丝勋章【{self.data.medal_name}】{self.data.medal_level}级"
                if self.data.type == 2 else
                f"{self.data.uid}的粉丝勋章【{self.data.medal_name}|{self.data.medal_level}】发生了type={self.data.type}"
            ),
            user=(self.data.uid, None),
            raw=self,
        )
