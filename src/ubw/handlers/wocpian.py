import logging

from rich.markup import escape

import blivedm

ROOM_IDS = [
    5252,  # 天堂
    # 17961,  # 赫萝老师
    42062,  # 瓶子君152
    # 81004,  # 艾尔莎_Channel
    913137,  # 噩梦
    1141542,  # 仙乐阅
    # 3428783,  # 绫濑光Official
    7688602,  # 花花Haya
    # 22898905,  # 珞璃Official
    27299825,  # 布莲雾
    # 27337779,  # 月见林林
]


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return msg, kwargs


logger = RichClientAdapter(logging.getLogger('wocpian'), {})


class PianHandler(blivedm.BaseHandler):
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
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [bright_red]{uname}[/]（uid={uid}）进入直播间")

    async def on_danmu_msg(self, client, message):
        uid = message.info.uid
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id

        if self.maybe_pian(uid, uname):
            logger.info(
                rf"\[[bright_cyan]{room_id}[/]] [bright_red]{uname}[/] ({uid=}): [bright_white]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        uname = message.data.uname
        uid = message.data.uid
        room_id = client.room_id

        if self.maybe_pian(uid, uname):
            logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 [bright_red]{uname}[/]（uid={uid}）被封禁")
        else:
            logger.warning(rf"\[[bright_cyan]{room_id}[/]] 用户 [cyan]{uname}[/]（uid={uid}）被封禁")
