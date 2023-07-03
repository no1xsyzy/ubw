import asyncio
import logging
import sys

from rich.markup import escape

import blivedm

ROOM_IDS = [
    81004,  # 艾尔莎_Channel
    21622680,  # 花玲
]

FAMOUS_PEOPLE = [
    777964,  # 奶茶☆
    1351379,  # 赫萝老师
    1521415,  # 艾尔莎_Channel
    2351778,  # 脚本作者，测试用
    5204356,  # 仙乐阅
    431412406,  # 虚研社长Official
    1816182565,  # 珞璃Official
]

logger = logging.getLogger('elza_karin')


async def listen_to_all(room_ids: list[int], handler: blivedm.BaseHandler):
    clients = {}
    for room_id in room_ids:
        clients[room_id] = blivedm.BLiveClient(room_id)

    for client in clients.values():
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(client.join() for client in clients.values()))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients.values()))


class MyHandler(blivedm.BaseHandler):
    def __init__(self, *, famous_people, **p):
        super().__init__(**p)
        self.famous_people = famous_people

    @property
    def famous_people(self):
        return self._famous_people

    @famous_people.setter
    def famous_people(self, value):
        self._famous_people = set(value)

    async def on_danmu_msg(self, client, message):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id

        if message.info.uid in self.famous_people:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [cyan]{uname}[/]: [bright_white]{escape(msg)}[/]")
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname}: [bright_white]{escape(msg)}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id
        logger.info(
            rf"\[[bright_cyan]{room_id}[/]] 直播间信息变更《[yellow]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {message}")

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname} \\[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 {message.data.uname}（uid={message.data.uid}）被封禁")

    async def on_live(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播开始")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播结束")


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(listen_to_all(ROOM_IDS, MyHandler(famous_people=FAMOUS_PEOPLE)))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
