from ._base import *


class LogInNoticeData(BaseModel):
    image_app: str
    image_web: str
    notice_msg: str


class LogInNoticeCommand(CommandModel):
    cmd: Literal['LOG_IN_NOTICE']
    data: LogInNoticeData

    def summarize(self) -> Summary:
        return Summary(
            t=self.ct,
            msg=self.data.notice_msg,
            user=None,
            raw=self,
        )
