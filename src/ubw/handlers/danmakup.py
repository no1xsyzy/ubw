import logging
import re
from functools import cached_property

import pydantic
from rich.markup import escape

import blivedm
from ubw.ui import Record, PlainText, User, RoomTitle, UI, ColorSeeSee


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
    show_interact_word: bool = False

    ui: UI | None = None


class DanmakuPHandler(blivedm.BaseHandler[DanmakuPHandlerSettings]):
    @cached_property
    def ui(self):
        if self.settings.ui is None:
            raise ValueError('this handler do not use ui')
        return self.settings.ui

    async def on_danmu_msg(self, client, message):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id
        if self.settings.ignore_danmaku is not None and self.settings.ignore_danmaku.match(msg):
            if self.settings.ui is not None:
                pass
            else:
                logger.debug(rf"This danmaku should be ignored, since it matches `ignore_danmaku`")
            if self.settings.show_ignore:
                if self.settings.ui is not None:
                    self.ui.add_record(Record(segments=[
                        ColorSeeSee(text=f"[{room_id}] "),
                        User(name=uname, uid=message.info.uid),
                        PlainText(text=f": "),
                        PlainText(text=msg),
                        PlainText(text=f" (ignored)"),
                    ]))
                else:
                    logger.info(
                        rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [grey]{escape(msg)}[/]")
        else:
            if self.settings.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f"说: "),
                    PlainText(text=msg),
                ]))
            else:
                logger.info(
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [bright_white]{escape(msg)}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id

        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"直播间信息变更"),
                RoomTitle(title=title, room_id=room_id),
                PlainText(text=f"，分区：{parent_area_name}/{area_name}"),
            ]))
        else:
            logger.info(
                rf"\[[bright_cyan]{room_id}[/]] "
                f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message: blivedm.models.WarningCommand):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"受到警告 {message.msg}"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [white on red]{message}[/]")

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=uname, uid=message.data.uid),
                PlainText(text=f"[¥{price}]: {msg}")
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname} \[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="用户被封禁"),
                User(name=message.data.uname, uid=message.data.uid),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                        f"[red]用户 {message.data.uname}（uid={message.data.uid}）被封禁[/]")

    async def on_live(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播开始"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                        "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Square For Stop}\N{VS16}直播结束"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")

    async def on_interact_word(self, client, model):
        if not self.settings.show_interact_word:
            return
        room_id = client.room_id
        c = ["", "进入", "关注", "分享", "特别关注", "互相关注"]
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=model.data.uname, uid=model.data.uid),
                PlainText(text=c[model.data.msg_type]),
                PlainText(text="了直播间"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 {model.data.uname}（uid={model.data.uid}）"
                        rf"{c[model.data.msg_type]}了直播间")
