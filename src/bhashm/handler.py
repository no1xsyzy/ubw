import asyncio
import logging
from datetime import datetime, timezone, timedelta

import aiocsv
import aiofiles
import aiofiles.os
from rich.markup import escape

import blivedm
from bilibili import get_info_by_room

live_start_times: dict[int, datetime | None] = {}


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        client = blivedm.ctx_client.get(None)
        if client is None:
            room_id = 'NO_ROOM'
        else:
            room_id = client.room_id
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return rf"\[[bright_cyan]{room_id}[/]] {msg}", kwargs


logger = RichClientAdapter(logging.getLogger('bhashm'), {})


async def get_live_start_time(room_id: int) -> datetime | None:
    return (await get_info_by_room(room_id)).room_info.live_start_time


def create_csv_writer(room_id: int):
    queue = asyncio.Queue()

    async def task():
        while True:
            dirname = f"output/bhashm/{room_id}"
            await aiofiles.os.makedirs(dirname, exist_ok=True)
            filename = f"{dirname}/{room_id}_{datetime.now(timezone(timedelta(seconds=8 * 3600))).strftime('%Y年%m月%d日%H点%M%S')}.csv"
            if await aiofiles.os.path.isfile(filename):
                mode = 'a'
            else:
                mode = 'w'

            async with aiofiles.open(filename, mode=mode, encoding='utf-8', newline="") as afp:
                writer = aiocsv.AsyncDictWriter(afp, ['time', 't', 'marker', 'symbol'])
                if mode == 'w':
                    await writer.writeheader()
                    await afp.flush()

                while True:
                    to_write = await queue.get()
                    if to_write == 'RESTART':
                        live_start_times[room_id] = await get_live_start_time(room_id)
                        queue.task_done()
                        break
                    else:
                        await writer.writerow(to_write)
                        await afp.flush()
                        queue.task_done()

    asyncio.create_task(task())
    return queue


async def listen_to_all(room_ids: list[int], famous_people: list[int]):
    clients = []
    for room_id in room_ids:
        client = blivedm.BLiveClient(room_id)
        # start time
        start_time_stamp = await get_live_start_time(room_id)
        live_start_times[room_id] = start_time_stamp
        # writer
        q = create_csv_writer(room_id)
        handler = HashMarkHandler(famous_people=famous_people, csv_queue=q)
        client.add_handler(handler)
        client.start()
        clients.append(client)

    try:
        await asyncio.gather(*(client.join() for client in clients))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients))


class HashMarkHandler(blivedm.BaseHandler):
    def __init__(self, *, famous_people, csv_queue, **p):
        super().__init__(**p)
        self.famous_people = famous_people
        self.csv_queue = csv_queue

    @property
    def famous_people(self):
        return self._famous_people

    @famous_people.setter
    def famous_people(self, value):
        self._famous_people = set(value)

    async def on_unknown_cmd(self, client, command):
        # in bhashm, locals are automatically logged
        import json
        cmd = command.get('cmd', None)
        logger.warning(f"unknown cmd {cmd}")
        await aiofiles.os.makedirs("output/unknown_cmd", exist_ok=True)
        async with aiofiles.open(f"output/unknown_cmd/{cmd}.json", mode='a', encoding='utf-8') as afp:
            await afp.write(json.dumps(command, indent=2))

    async def on_danmu_msg(self, client, message):
        uname = message.info.uname
        msg = message.info.msg
        time = message.info.timestamp
        room_id = client.room_id
        if live_start_times[room_id] is not None:
            t = str(time - live_start_times[room_id]).split(".")[0]
            live_start_suffix = f" ({t} from live start)"
        else:
            t = live_start_suffix = ""

        if msg.startswith("#"):
            logger.info(f"[blue]marker[/] {uname}: [bright_white]{escape(msg)}[/][bright_green]{live_start_suffix}[/]")
            await self.csv_queue.put({
                'time': (
                    time.astimezone(timezone(timedelta(seconds=8 * 3600)))
                    .replace(tzinfo=None)
                    .isoformat(sep=" ", timespec='seconds')),
                't': t, 'marker': uname, 'symbol': msg
            })
        elif message.info.uid in self.famous_people:
            logger.info(f"[red]famous[/] {uname}: [bright_white]{escape(msg)}[/][bright_green]{live_start_suffix}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        logger.info(f"直播间信息变更《[yellow]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message):
        logger.info(message)

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        logger.info(f"{uname} \\[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        logger.info(f"用户 {message.data.uname}（uid={message.data.uid}）被封禁")

    async def on_live(self, client, message):
        logger.info("直播开始")
        await self.csv_queue.put('RESTART')

    async def on_preparing(self, client, message):
        logger.info("直播结束")
        await self.csv_queue.put('RESTART')

    async def on_notice_msg(self, client, model):
        if model.msg_type in {1, 2}:
            return
        logger.info(f"[{model.msg_type}] {escape(model.msg_common)}")
