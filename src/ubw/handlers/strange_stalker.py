import logging
import re

from rich.markup import escape

import blivedm


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return msg, kwargs


logger = RichClientAdapter(logging.getLogger('strange_stalker'), {})


class StrangeStalkerHandlerSettings(blivedm.HandlerSettings):
    uids: list[int] = []
    regex: re.Pattern | None = None
    ignore_danmaku: re.Pattern | None = None


class StrangeStalkerHandler(blivedm.BaseHandler[StrangeStalkerHandlerSettings]):
    async def on_summary(self, client, summary):
        json = summary.raw.json(ensure_ascii=False)
        if self.settings.regex is not None and self.settings.regex.match(json):
            logger.info(rf"[{summary.room_id}] {summary.msg} ({summary.raw.cmd})")

    async def on_maybe_summarizer(self, client, model):
        json = model.json(ensure_ascii=False)
        if self.settings.regex is not None and self.settings.regex.match(json):
            logger.info(rf"\[[bright_cyan]{client.room_id}[/]] " + json)

    async def on_danmu_msg(self, client, message):
        if message.info.uid not in self.settings.uids and not self.settings.regex.match(message.info.msg):
            return
        if self.settings.ignore_danmaku is not None and self.settings.ignore_danmaku.match(message.info.msg):
            return
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
            rf"\[[bright_cyan]{room_id}[/]] "
            f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {message}")

    async def on_live(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                    "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")

    async def on_interact_word(self, client, model):
        if model.data.uid not in self.settings.uids:
            return
        return await super().on_interact_word(client, model)

    async def on_anchor_helper_danmu(self, client, model):
        room_id = client.room_id
        logger.info(rf"\[[bright_cyan]{room_id}[/]] {model.data.sender}: {model.data.msg}")
