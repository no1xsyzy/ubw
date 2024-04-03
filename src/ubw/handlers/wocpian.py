"""
(archived) 检测片哥并作出提示，因片哥消失而收容。
"""

from ._base import *


class PianHandler(BaseHandler):
    cls: Literal['pian'] = 'pian'

    @staticmethod
    def maybe_pian(uid: int, uname: str) -> bool:
        return uid > 3493280000000000 and uname.startswith("bili_") and uname[5:].isnumeric()

    async def on_maybe_summarizer(self, client, model):
        pass

    async def on_interact_word(self, client, model):
        uid = model.data.uid
        uname = model.data.uname
        room_id = client.room_id

        if self.maybe_pian(uid, uname) and model.data.msg_type == 1:
            rich.print(
                rf"\[{model.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] [bright_red]{uname}[/]（uid={uid}）进入直播间")

    async def on_danmu_msg(self, client, message):
        uid = message.info.uid
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id

        if self.maybe_pian(uid, uname):
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] [bright_red]{uname}[/] ({uid=}): [bright_white]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        uname = message.data.uname
        uid = message.data.uid
        room_id = client.room_id

        color = 'bright_red' if self.maybe_pian(uid, uname) else 'cyan'

        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] 用户 [{color}]{uname}[/] (uid={uid}) 被封禁")
