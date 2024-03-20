from ._base import *


class UserToastMsgData(BaseModel):
    anchor_show: bool
    color: Color
    dmscore: int
    effect_id: int
    end_time: datetime
    face_effect_id: int
    gift_id: int
    guard_level: int
    is_show: int
    num: int
    op_type: int
    payflow_id: str
    price: int
    """金瓜子"""
    role_name: str
    room_effect_id: int
    start_time: datetime
    svga_block: int
    target_guard_count: int
    toast_msg: str
    uid: int
    unit: str
    user_show: bool
    username: str

    group_name: str = ''
    group_op_type: int = 0
    group_role_name: str = ''
    is_group: int = 0
    room_group_effect_id: int = 1337


class UserToastMsgCommand(CommandModel):
    cmd: Literal['USER_TOAST_MSG']
    data: UserToastMsgData

    def summarize(self):
        return Summary(
            t=self.data.start_time,
            msg=self.data.toast_msg,
            user=(self.data.uid, self.data.username),
            price=self.data.price // 1000,
            raw=self,
        )
