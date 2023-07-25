import asyncio
import logging
import sys

import sentry_sdk
import typer
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


logger = RichClientAdapter(logging.getLogger('danmakup'), {})


class MyHandler(blivedm.BaseHandler):
    async def on_danmu_msg(self, client, message):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id
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
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname} \[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 {message.data.uname}（uid={message.data.uid}）被封禁")

    async def on_live(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播开始")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] 直播结束")


def main(room_ids: list[int]):
    try:
        asyncio.run(blivedm.listen_to_all(room_ids, MyHandler()))
    except KeyboardInterrupt:
        print("用户中断", file=sys.stdout)


if __name__ == '__main__':
    typer.run(main)
