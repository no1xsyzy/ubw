import asyncio
import logging
import sys

import sentry_sdk
from rich.logging import RichHandler
from rich.markup import escape

import blivedm

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


logger = RichClientAdapter(logging.getLogger('find_elza'), {})


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
    async def on_unknown_cmd(self, client, command):
        import json
        import aiofiles.os
        cmd = command.get('cmd', None)
        # logger.warning(f"unknown cmd {cmd}")
        await aiofiles.os.makedirs("output/unknown_cmd", exist_ok=True)
        async with aiofiles.open(f"output/unknown_cmd/{cmd}.json", mode='a', encoding='utf-8') as afp:
            await afp.write(json.dumps(command, indent=2, ensure_ascii=False))
        sentry_sdk.capture_event(
            event={'level': 'warning', 'message': f"unknown cmd {cmd}"},
            user={'id': client.room_id},
            contexts={'command': {'command': command}},
            tags={'module': 'bhashm', 'unknown_cmd': "yes", 'cmd': cmd, 'room_id': client.room_id},
        )

    async def on_summary(self, client, summary):
        if summary.user is not None and summary.user[0] in [1521415, 2351778]:
            logger.info(rf"{summary.msg} ({summary.raw.__class__.__name__})")

    async def on_danmu_msg(self, client, message):
        if message.info.uid in [1521415, 2351778]:
            logger.info(rf"\[[bright_cyan]{client.room_id}[/]] "
                        rf"[cyan]{message.info.uname}[/]: [bright_white]{escape(message.info.msg)}[/]")

    async def on_card_msg(self, client, model):
        logger.info(rf"{model.data.card_data.uid}进入了{model.data.card_data.room_id} (CardMsgCommand)")

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

    async def on_live(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播开始")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播结束")


def main():
    try:
        OPS = [730215, 81004]
        asyncio.run(listen_to_all(OPS, MyHandler()))
    except KeyboardInterrupt:
        print("用户中断", file=sys.stdout)


if __name__ == '__main__':
    main()
