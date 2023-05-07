import asyncio
import logging
import sys

import sentry_sdk
from rich.logging import RichHandler
from rich.markup import escape

import blivedm

ROOM_IDS = [
    5252,  # 天堂
    17961,  # 赫萝老师
    42062,  # 瓶子君152
    81004,  # 艾尔莎_Channel
    913137,  # 噩梦
    1141542,  # 仙乐阅
    3428783,  # 绫濑光Official
    7688602,  # 花花Haya
    22898905,  # 珞璃Official
    27299825,  # 布莲雾
    27337779,  # 月见林林
]

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(
        # rich_tracebacks=True,
        # tracebacks_show_locals=True,
        tracebacks_suppress=['logging', 'rich'],
        show_path=False,
    )],
)
sentry_sdk.init(
    dsn="https://f6bcb89a35fb438f81eb2d7679c5ded0@o4504791466835968.ingest.sentry.io/4504791473127424",
    traces_sample_rate=1.0,
)


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return msg, kwargs


logger = RichClientAdapter(logging.getLogger('wocpian'), {})


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


class PianHandler(blivedm.BaseHandler):
    @staticmethod
    def maybe_pian(uid: int, uname: str) -> bool:
        return uid > 3493280000000000 and uname.startswith("bili_") and uname[5:].isnumeric()

    async def on_unknown_cmd(self, client, command):
        import json
        import aiofiles.os
        cmd = command.get('cmd', None)
        logger.warning(f"unknown cmd {cmd}")
        await aiofiles.os.makedirs("output/unknown_cmd", exist_ok=True)
        async with aiofiles.open(f"output/unknown_cmd/{cmd}.json", mode='a', encoding='utf-8') as afp:
            await afp.write(json.dumps(command, indent=2))
        sentry_sdk.capture_event(
            event={'level': 'warning', 'message': f"unknown cmd {cmd}"},
            user={'id': client.room_id},
            contexts={'command': {'command': command}},
            tags={'module': 'bhashm', 'unknown_cmd': "yes", 'cmd': cmd, 'room_id': client.room_id},
        )

    async def on_else(self, client, model):
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
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [bright_red]{uname}[/]: [bright_white]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        uname = message.data.uname
        uid = message.data.uid
        room_id = client.room_id

        if self.maybe_pian(uid, uname):
            logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 [bright_red]{uname}[/]（uid={uid}）被封禁")
        else:
            logger.warning(rf"\[[bright_cyan]{room_id}[/]] 用户 [cyan]{uname}[/]（uid={uid}）被封禁")


if __name__ == '__main__':
    try:
        asyncio.run(listen_to_all(ROOM_IDS, PianHandler()))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
