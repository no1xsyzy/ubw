import re

from ._base import *


class StrangeStalkerHandler(BaseHandler):
    cls: Literal['strange_stalker'] = 'strange_stalker'
    uids: list[int] = []
    regex: re.Pattern | None = None
    ignore_danmaku: re.Pattern | None = None

    async def on_summary(self, client, summary):
        json = summary.raw.model_dump_json()
        if self.regex is not None and self.regex.match(json):
            rich.print(
                rf"\[{summary.raw.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"[{summary.room_id}] {summary.msg} ({summary.raw.cmd})")

    async def on_maybe_summarizer(self, client, model):
        json = model.model_dump_json()
        if self.regex is not None and self.regex.match(json):
            rich.print(
                rf"\[{model.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{client.room_id}[/]] " + json)

    async def on_danmu_msg(self, client, message):
        if message.info.uid not in self.uids and not self.regex.match(message.info.msg):
            return
        if self.ignore_danmaku is not None and self.ignore_danmaku.match(message.info.msg):
            return
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{client.room_id}[/]] "
            rf"[cyan]{message.info.uname}[/]: [bright_white]{escape(message.info.msg)}[/]")

    async def on_card_msg(self, client, model):
        rich.print(
            rf"\[{model.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"{model.data.card_data.uid}进入了{model.data.card_data.room_id} (CardMsgCommand)")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message):
        room_id = client.room_id
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] {message}")

    async def on_live(self, client, message):
        room_id = client.room_id
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")

    async def on_interact_word(self, client, model):
        if model.data.uid not in self.uids:
            return
        return await super().on_interact_word(client, model)

    async def on_anchor_helper_danmu(self, client, model):
        room_id = client.room_id
        rich.print(
            rf"\[{model.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] {model.data.sender}: {model.data.msg}")
