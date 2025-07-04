import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Annotated

from pydantic import Field
from typing_extensions import Doc

from ubw import models
from ubw.clients import BilibiliCookieClient, BilibiliClient, WSWebCookieLiveClient
from ubw.handlers.observe import ObserverHandler
from ubw.push.qmsg import QMsgPusher
from ubw.push.serverchan import ServerChanPusher, ServerChanMessage
from ubw.ui.stream_view import *
from ._base import *

logger: logging.Logger = logging.getLogger('observer')


def key(dyn: models.DynamicItem):
    return 0 if dyn.is_topped else 1, dyn.pub_date


class ObserverApp(InitLoopFinalizeApp):
    cls: Literal['observer'] = 'observer'

    # high config
    uid: int

    # low config
    dynamic_poll_interval: float = 60
    exponential_delay_base: Annotated[float, Doc('use exponential delay with this base')] = 2.0

    # DI
    bilibili_client: BilibiliClient = Field(default_factory=BilibiliCookieClient)
    bilibili_client_owner: bool = True
    ui: StreamView = Richy()
    owned_ui: bool = True
    server_chan: ServerChanPusher | None = None
    owned_server_chan: bool = True
    qmsg: QMsgPusher | None = None
    owned_qmsg: bool = True

    # states
    last_got: set = Field(default_factory=set)
    room_id: int = 0
    name: str = ""

    # runtime
    _live_handler: ObserverHandler | None = None
    _live_client: WSWebCookieLiveClient | None = None
    _task: asyncio.Task | None = None
    _fail_count: int = 0

    async def _init(self):
        acc_info = None
        if self.bilibili_client_owner:
            await self.bilibili_client.read_cookie()  # checkpoint1
        if self.owned_ui:
            await self.ui.start()
        if self.room_id == 0:
            self.room_id = (
                    acc_info or (acc_info := await self.bilibili_client.get_account_info(self.uid))).live_room_id
        if self.name == "":
            self.name = (acc_info or (acc_info := await self.bilibili_client.get_account_info(self.uid))).name
        self._live_client = WSWebCookieLiveClient(
            room_id=self.room_id,
            bilibili_client=self.bilibili_client, bilibili_client_owner=False,
        )
        self._live_handler = ObserverHandler(
            room_id=self.room_id,
            ui=self.ui, owned_ui=False,
            bilibili_client=self.bilibili_client, bilibili_client_owner=False,
            server_chan=self.server_chan, owned_server_chan=False,
            qmsg=self.qmsg, owned_qmsg=False,
        )
        self._live_client.add_handler(self._live_handler)
        await self._live_handler.start(self._live_client)
        await self._live_client.start()
        await self._fetch_print_update(True)
        await self.ui.add_record(Record(segments=[PlainText(text=" ===== 以上为历史消息 ===== ")]))

    async def _fetch_print_update(self, init):
        s = await self.bilibili_client.get_user_dynamic(self.uid)
        this_got = {item.id_str for item in s.items}
        for item in sorted(s.items, key=key):
            if item.id_str not in self.last_got:
                if item.is_topped:
                    await self.ui.add_record(Record(segments=[
                        Anchor(text="置顶动态", href=item.jump_url),
                        PlainText(text=" "),
                        PlainText(text=item.text),
                    ], time=item.pub_date))
                    if not init:
                        await self._deal_with_push(f"{self.name} 有新置顶动态", item)
                elif (datetime.now().astimezone() - item.pub_date) > timedelta(days=2):
                    pass
                elif item.is_video:
                    await self.ui.add_record(Record(segments=[
                        Anchor(text="发布视频", href=item.jump_url),
                        PlainText(text=" "),
                        PlainText(text=item.text),
                    ], time=item.pub_date))
                    if not init:
                        await self._deal_with_push(f"{self.name} 发布视频", item)
                elif item.is_live:
                    await self.ui.add_record(Record(segments=[
                        Anchor(text="直播动态", href=item.jump_url),
                        PlainText(text=" "),
                        PlainText(text=item.text),
                    ], time=item.pub_date))
                elif item.is_forward:
                    segments = [
                        Anchor(text="转发动态", href=item.jump_url),
                        PlainText(text=" "),
                        PlainText(text=item.text),
                        PlainText(text="\n"),
                        Anchor(text="原动态", href=item.orig.jump_url),
                        PlainText(text=" "),
                    ]
                    if item.orig.id_str in this_got | self.last_got and len(item.orig.text) > 40:
                        segments.append(PlainText(text=item.orig.text[:37] + "..."))
                    else:
                        segments.append(PlainText(text=item.orig.text))
                    await self.ui.add_record(Record(segments=segments, time=item.pub_date))
                    if not init:
                        await self._deal_with_push(f"{self.name} 转发动态", item)
                else:
                    await self.ui.add_record(Record(segments=[
                        Anchor(text="发布动态", href=item.jump_url),
                        PlainText(text=" "),
                        PlainText(text=item.text),
                    ], time=item.pub_date))
                    if not init:
                        await self._deal_with_push(f"{self.name} 发布动态", item)
        self.last_got = this_got

    async def _deal_with_push(self, title, item: models.DynamicItem):
        if self.server_chan is not None:
            await self.server_chan.push(ServerChanMessage(title=title, desp=item.markdown))
        if self.qmsg is not None:
            await self.qmsg.push(title + "\n" + re.sub(r"https?://[\w\-.]+/[^\s()\[\]{}]+", "<URL>", item.text))

    async def _loop(self):
        await asyncio.sleep(self.dynamic_poll_interval * (self.exponential_delay_base ** self._fail_count))
        try:
            await self._fetch_print_update(False)
            self._fail_count = 0
        except Exception as e:
            logger.exception("exception in _fetch_print_update", exc_info=e)
            self._fail_count += 1
            if self._fail_count > 5:
                raise

    async def _finalize(self):
        if self._live_client is not None:
            await self._live_client.stop()
        if self._live_handler is not None:
            await self._live_handler.stop()
        if self.owned_ui:
            await self.ui.stop()

    async def close(self):
        if self._live_client is not None:
            await self._live_client.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
        if self.server_chan is not None and self.owned_server_chan:
            await self.server_chan.close()
        if self.qmsg is not None and self.owned_qmsg:
            await self.qmsg.close()
