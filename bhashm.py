import asyncio
from datetime import datetime
import logging
from pathlib import Path, _ignore_error as pathlib_ignore_error

import aiofiles
import aiofiles.os
import aiocsv
import aiohttp
from rich import print
from rich.logging import RichHandler

import blivedm

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger('bhashm')

ROOM_IDS = [81004, 730215]

live_start_times = {}
csv_write_queues = {}


async def main():
    await listen_to_all()


async def get_live_start_time(room_id, fallback_to_now=False):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}") as resp:
            jso = await resp.json()
            live_start_time = jso['data']['room_info']['live_start_time']
            if fallback_to_now and live_start_time == 0:
                live_start_time = int(datetime.now().timestamp())
            return live_start_time


async def csv_writer(room_id, start):
    start = datetime.fromtimestamp(start)
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
                    start = live_start_times[room_id] = datetime.fromtimestamp(await get_live_start_time(room_id, True))
                    queue.task_done()
                    break
                else:
                    await writer.writerow(to_write)
                    await afp.flush()
                    queue.task_done()


async def listen_to_all():
    script_start = int(datetime.now().timestamp())
    clients = {}
    for room_id in ROOM_IDS:
        clients[room_id] = blivedm.BLiveClient(room_id)
        # start time
        start_time_stamp = await get_live_start_time(room_id)
        live_start_times[room_id] = datetime.fromtimestamp(start_time_stamp) if start_time_stamp != 0 else None
        # writer
        asyncio.create_task(csv_writer(room_id, script_start))

    handler = HashMarkHandler()
    # print(handler._CMD_CALLBACK_DICT)

    for client in clients.values():
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(client.join() for client in clients.values()))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients.values()))


class HashMarkHandler(blivedm.BaseHandler):
    async def on_danmaku(self, client, message):
        if message.msg.startswith("#"):
            room_id = client.room_id
            time = datetime.fromtimestamp(message.timestamp//1000)
            marker = message.uname
            symbol = message.msg
            if live_start_times[room_id] is not None:
                t = str(time - live_start_times[room_id])
                print(f"[{time}] {marker}: {symbol} @ {room_id} ({t} from live start)")
                await csv_write_queues[room_id].put({'time': time, 't': t, 'marker': marker, 'symbol': symbol})
            else:
                print(f"[{time}] {marker}: {symbol} @ {room_id}")
                await csv_write_queues[room_id].put({'time': time, 't': "", 'marker': marker, 'symbol': symbol})


    async def on_room_change(self, client, message):
        logger.info(message)

    async def on_live(self, client, message):
        room_id = client.room_id
        await csv_write_queues[room_id].put('RESTART')

    async def on_preparing(self, client, message):
        room_id = client.room_id
        await csv_write_queues[room_id].put('RESTART')


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
