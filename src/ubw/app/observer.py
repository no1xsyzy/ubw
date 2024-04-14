import asyncio
from datetime import datetime, timedelta

import rich
from pydantic import Field
from rich.markup import escape

from ubw.clients import BilibiliCookieClient, BilibiliClient, WSWebCookieLiveClient
from ubw.handlers.observe import Observer
from ._base import *
from .. import models


def key(dyn: models.DynamicItem):
    return 0 if dyn.is_topped else 1, dyn.pub_date


class ObserverApp(InitLoopFinalizeApp):
    cls: Literal['observer'] = 'observer'

    uid: int
    bilibili_client: BilibiliClient = Field(default_factory=BilibiliCookieClient)
    bilibili_client_owner: bool = True

    dynamic_poll_interval: float = 60

    _room_id: int = 0
    _live_handler: Observer | None = None
    _task: asyncio.Task | None = None
    _live_client: WSWebCookieLiveClient | None = None
    _last_got: set | None = None

    async def _init(self):
        if self.bilibili_client_owner:
            await self.bilibili_client.read_cookie()  # checkpoint1
        self._room_id = (await self.bilibili_client.get_account_info(self.uid)).live_room_id
        self._live_client = WSWebCookieLiveClient(
            room_id=self._room_id,
            bilibili_client=self.bilibili_client, bilibili_client_owner=False
        )
        self._live_handler = Observer(room_id=self._room_id)
        self._live_client.add_handler(self._live_handler)
        await self._live_handler.start(self._live_client)
        await self._live_client.start()
        if self._last_got is None:
            self._last_got = set()
        await self._fetch_print_update()
        rich.print(" ===== 以上为历史消息 ===== ")

    async def _fetch_print_update(self):
        s = await self.bilibili_client.get_user_dynamic(self.uid)  # checkpoint3
        for item in sorted(s.items, key=key):
            if item.id_str not in self._last_got:
                if item.is_topped:
                    rich.print(rf"\[{item.pub_date.strftime('%Y-%m-%d %H:%M:%S')}] "
                               f"[bright_blue]置顶动态[/]：{escape(item.text)}"
                               f" [link {item.jump_url}]链接[/]")
                elif (datetime.now() - item.pub_date) > timedelta(days=2):
                    pass
                else:
                    rich.print(rf"\[{item.pub_date.strftime('%Y-%m-%d %H:%M:%S')}] "
                               f"发布动态：{escape(item.text)}"
                               f" [link {item.jump_url}]链接[/]")
        self._last_got = {item.id_str for item in s.items}

    async def _loop(self):
        await asyncio.sleep(self.dynamic_poll_interval)
        await self._fetch_print_update()

    async def _finalize(self):
        if self._live_client is not None:
            try:
                await self._live_client.stop()
            except asyncio.CancelledError:
                pass

    async def close(self):
        await self._live_client.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
