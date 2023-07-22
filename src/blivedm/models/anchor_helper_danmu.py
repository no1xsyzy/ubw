from ._base import *


class AnchorHelperDanmuData(BaseModel):
    button_label: int
    button_name: str
    button_platform: int
    button_target: str
    msg: str
    platform: int
    report: int
    report_type: str
    sender: str


class AnchorHelperDanmuCommand(CommandModel):
    """这个command似乎会泄漏主播的收益？"""
    cmd: Literal['ANCHOR_HELPER_DANMU']
    data: AnchorHelperDanmuData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=f"{self.data.sender}: {self.data.msg}",
            user=(self.data.report, None),
            room_id=None,
            raw=self,
        )
