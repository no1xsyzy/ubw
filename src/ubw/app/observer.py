import asyncio

import rich
from pydantic import Field
from rich.markup import escape

from ubw.clients import BilibiliCookieClient, BilibiliClient, WSWebCookieLiveClient
from ubw.handlers.observe import Observer
from ._base import *


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
        self._live_handler.start(self._live_client)
        await self._live_handler.astart(self._live_client)  # checkpoint2
        self._live_client.start()
        await self._fetch_print_update()
        print(" ===== 以上为历史消息 ===== ")

    async def _fetch_print_update(self):
        if self._last_got is None:
            self._last_got = set()
        s = await self.bilibili_client.get_user_dynamic(self.uid)  # checkpoint3
        for item in reversed(s.items):
            if item.id_str not in self._last_got:
                rich.print(rf"\[{item.pub_date.strftime('%Y-%m-%d %H:%M:%S')}] "
                           f"发布动态：{escape(item.text)}"
                           f" [link {item.jump_url}]链接[/]")
        self._last_got = {item.id_str for item in s.items}

    async def _loop(self):
        await self._fetch_print_update()
        await asyncio.sleep(self.dynamic_poll_interval)

    async def _finalize(self):
        try:
            if self._live_client is not None:
                stop = self._live_client.stop()
                if stop is not None:
                    await stop
        except asyncio.CancelledError:
            pass

    async def close(self):
        await self._live_client.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
