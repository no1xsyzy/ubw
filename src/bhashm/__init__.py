import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import aiocsv
import aiofiles
import aiofiles.os
import aiohttp
from rich.markup import escape

import blivedm
from blivedm import ctx_client

live_start_times: dict[int, Optional[datetime]] = {}
csv_write_queues = {}


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        client = ctx_client.get(None)
        if client is None:
            room_id = 'NO_ROOM'
        else:
            room_id = client.room_id
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return rf"\[[bright_cyan]{room_id}[/]] {msg}", kwargs


logger = RichClientAdapter(logging.getLogger('bhashm'), {})


async def get_live_start_time(room_id: int, fallback_to_now=False) -> Optional[datetime]:
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}") as resp:
            jso = await resp.json()
            live_start_time: int = jso['data']['room_info']['live_start_time']
            if live_start_time == 0:
                if fallback_to_now:
                    return datetime.now(timezone(timedelta(seconds=8*3600)))
                else:
                    return None
            return datetime.fromtimestamp(live_start_time, timezone(timedelta(seconds=8*3600)))


async def csv_writer(room_id: int, start: datetime):
    start = start
    while True:
        dirname = f"output/{room_id}"
        await aiofiles.os.makedirs(dirname, exist_ok=True)
        filename = f"output/{room_id}/{room_id}_{start.strftime('%Y年%m月%d日%H点%M%S')}.csv"
        if await aiofiles.os.path.isfile(filename):
            mode = 'a'
        else:
            mode = 'w'

        async with aiofiles.open(filename, mode=mode, encoding='utf-8', newline="") as afp:
            writer = aiocsv.AsyncDictWriter(afp, ['time', 't', 'marker', 'symbol'])
            if mode == 'w':
                await writer.writeheader()
                await afp.flush()
            queue = asyncio.Queue()
            csv_write_queues[room_id] = queue
            while True:
                to_write = await queue.get()
                if to_write == 'RESTART':
                    start = live_start_times[room_id] = await get_live_start_time(room_id, True)
                    queue.task_done()
                    break
                else:
                    await writer.writerow(to_write)
                    await afp.flush()
                    queue.task_done()


async def listen_to_all(room_ids: list[int], famous_people: list[int]):
    script_start = datetime.now(timezone(timedelta(seconds=8*3600)))
    clients = {}
    for room_id in room_ids:
        clients[room_id] = blivedm.BLiveClient(room_id)
        # start time
        start_time_stamp = await get_live_start_time(room_id)
        live_start_times[room_id] = start_time_stamp
        # writer
        asyncio.create_task(csv_writer(room_id, script_start))

    handler = HashMarkHandler(famous_people=famous_people)
    # print(handler._CMD_CALLBACK_DICT)

    for client in clients.values():
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(client.join() for client in clients.values()))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients.values()))


class HashMarkHandler(blivedm.BaseHandler):
    def __init__(self, *, famous_people, **p):
        super().__init__()
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
        time = message.info.timestamp
        room_id = client.room_id
        if live_start_times[room_id] is not None:
            t = str(time - live_start_times[room_id])
            live_start_suffix = f" ({t} from live start)"
        else:
            t = live_start_suffix = ""

        if msg.startswith("#"):
            logger.info(f"[blue]marker[/] {uname}: [bright_white]{escape(msg)}[/][bright_green]{live_start_suffix}[/]")
            await csv_write_queues[room_id].put({'time': time, 't': t, 'marker': uname, 'symbol': msg})
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
        logger.info(f"{uname} \\[[bright_cyan]¥{price}[/]]: [{color}]{msg}[/]")

    async def on_room_block_msg(self, client, message):
        logger.info(f"用户 {message.data.uname}（uid={message.data.uid}）被封禁")

    async def on_live(self, client, message):
        room_id = client.room_id
        await csv_write_queues[room_id].put('RESTART')

    async def on_preparing(self, client, message):
        room_id = client.room_id
        await csv_write_queues[room_id].put('RESTART')
