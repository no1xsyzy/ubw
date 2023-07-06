from ._base import *


class MessageboxUserGainMedalData(BaseModel):
    type: int
    uid: int
    up_uid: int
    medal_id: int
    medal_name: str
    medal_level: int
    medal_color: int
    medal_color_start: int
    medal_color_end: int
    medal_color_border: int
    msg_title: str
    msg_content: str
    normal_color: int
    highlight_color: int
    intimacy: int
    next_intimacy: int
    today_feed: int
    day_limit: int
    is_wear: int
    guard_level: int
    is_received: int
    is_lighted: int
    toast: str
    fan_name: str


class MessageboxUserGainMedalCommand(CommandModel):
    cmd: Literal['MESSAGEBOX_USER_GAIN_MEDAL']
    data: MessageboxUserGainMedalData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.data.msg_title,
            user=(self.data.uid, self.data.fan_name),
            raw=self,
        )
