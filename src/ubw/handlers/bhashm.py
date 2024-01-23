import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Literal

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


def create_csv_writer(room_id: int) -> asyncio.Queue:
    queue = asyncio.Queue()

    async def task():
        while True:
            dirname = f"output/bhashm/{room_id}"
            await aiofiles.os.makedirs(dirname, exist_ok=True)
            filename = f"{dirname}/{room_id}_{datetime.now(timezone(timedelta(seconds=8 * 3600))).strftime('%Y年%m月%d日%H点%M%S')}.csv"
            mode: Literal['a', 'w']
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


class HashMarkHandlerSettings(blivedm.HandlerSettings):
    famous_people: list[int] = []


class HashMarkHandler(blivedm.BaseHandler[HashMarkHandlerSettings]):
    def __init__(self, settings):
        super().__init__(settings)
        self.csv_queues: dict[int, asyncio.Queue] = {}

    def get_csv_queue_for(self, room_id) -> asyncio.Queue:
        if room_id not in self.csv_queues:
            self.csv_queues[room_id] = create_csv_writer(room_id)
        return self.csv_queues[room_id]

    async def on_summary(self, client, summary):
        line = f"{summary.user[1]}(uid={summary.user[0]}): {escape(summary.msg)}"
        if summary.price:
            line += rf" \[{summary.price}]"
        logger.info(line)

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
            await self.get_csv_queue_for(room_id).put({
                'time': (
                    time.astimezone(timezone(timedelta(seconds=8 * 3600)))
                    .replace(tzinfo=None)
                    .isoformat(sep=" ", timespec='seconds')),
                't': t, 'marker': uname, 'symbol': msg
            })
        elif message.info.uid in self.settings.famous_people:
            logger.info(f"[red]famous[/] {uname}: [bright_white]{escape(msg)}[/][bright_green]{live_start_suffix}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        logger.info(f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

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
        logger.info("[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")
        await self.get_csv_queue_for(client.room_id).put('RESTART')

    async def on_preparing(self, client, message):
        logger.info("[black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")
        await self.get_csv_queue_for(client.room_id).put('RESTART')

    async def on_notice_msg(self, client, model):
        if model.msg_type in {1, 2}:
            return
        if model.msg_common.strip():
            logger.info(f"[{model.msg_type}] {escape(model.msg_common)}")
        if model.msg_self.strip():
            logger.info(f"[{model.msg_type}] {escape(model.msg_self)}")
        else:
            logger.info(model)
