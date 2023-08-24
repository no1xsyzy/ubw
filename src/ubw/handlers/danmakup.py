import logging
import re

import pydantic
from rich.markup import escape

import blivedm


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return msg, kwargs


logger = RichClientAdapter(logging.getLogger('danmakup'), {})


def try_compile(cls, reg: re.Pattern | str | None) -> re.Pattern | None:
    if isinstance(reg, str):
        return re.compile(reg)
    else:
        return reg


class DanmakuPHandlerSettings(blivedm.HandlerSettings):
    ignore_danmaku: re.Pattern | None = None
    show_ignore: bool = False
    validate_ignore_danmaku = pydantic.validator('ignore_danmaku', pre=True, allow_reuse=True)(try_compile)


class DanmakuPHandler(blivedm.BaseHandler[DanmakuPHandlerSettings]):
    async def on_danmu_msg(self, client, message):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id
        if self.settings.ignore_danmaku is not None and self.settings.ignore_danmaku.match(msg):
            logger.debug(rf"This danmaku should be ignored, since it matches `ignore_danmaku`")
            if self.settings.show_ignore:
                logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname}: [grey]{escape(msg)}[/]")
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname}: [bright_white]{escape(msg)}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id
        logger.info(
            rf"\[[bright_cyan]{room_id}[/]] "
            f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] [white on red]{message}[/]")

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname} \[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                    f"[red]用户 {message.data.uname}（uid={message.data.uid}）被封禁[/]")

    async def on_live(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                    "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")
