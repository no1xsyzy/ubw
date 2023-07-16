import asyncio
import logging
import re
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


async def listen_to_all(room_ids: list[int], handler: blivedm.HandlerInterface):
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
    def __init__(self, uids=None, reg=None, **p):
        super().__init__(**p)
        self.uids = uids or []
        if isinstance(reg, str):
            self.reg = re.compile(reg)
        elif isinstance(reg, re.Pattern):
            self.reg = re
        else:
            self.reg = re.compile('')

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
        logger.info(command)

    async def on_else(self, client, model):
        json = model.json(ensure_ascii=False)
        if self.reg.match(json):
            if isinstance(model, blivedm.models.Summarizer):
                summary = model.summarize()
                logger.info(rf"[{summary.room_id}] {summary.msg} ({summary.raw.cmd})")
            else:
                logger.info(rf"\[[bright_cyan]{client.room_id}[/]] " + json)

    async def on_danmu_msg(self, client, message):
        if message.info.uid in self.uids:
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

    async def on_stop_live_room_list(self, client, model):
        pass

    async def on_heartbeat(self, client, message):
        pass

    async def on_online_rank_count(self, client, model):
        pass

    async def on_interact_word(self, client, model):
        if model.data.uid not in self.uids:
            return
        return super().on_interact_word(client, model)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--regex', default='')
    parser.add_argument('-u', '--uids', action='append', type=int)
    parser.add_argument('rooms', nargs='+', type=int)
    args = parser.parse_args()
    try:
        asyncio.run(listen_to_all(args.rooms, MyHandler(uids=args.uids, reg=args.regex)))
        # asyncio.run(listen_to_all([int(x) for x in sys.argv[1:]],
        #                           MyHandler(uids=[1521415, 2351778],
        #                                     reg='2351778|1521415|橘枳橼|艾尔莎|81004|730215|王飘')))
    except KeyboardInterrupt:
        print("用户中断", file=sys.stdout)


if __name__ == '__main__':
    main()
