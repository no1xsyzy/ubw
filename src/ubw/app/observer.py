import asyncio

import rich
from pydantic import Field
from rich.markup import escape

from ubw.clients import BilibiliCookieClient, BilibiliClient, WSWebCookieLiveClient
from ubw.handlers.observe import Observer
from ._base import *


class ObserverApp(BaseApp):
    cls: Literal['observer'] = 'observer'

    uid: int
    bilibili_client: BilibiliClient = Field(default_factory=BilibiliCookieClient)
    bilibili_client_owner: bool = True

    dynamic_poll_interval: float = 60

    _room_id: int = 0
    _live_handler: Observer | None = None
    _task: asyncio.Task | None = None
    _live_client: WSWebCookieLiveClient | None = None

    async def get_room_id(self):
        if self._room_id == 0:
            acc = await self.bilibili_client.get_account_info(self.uid)
            self._room_id = acc.live_room_id
        return self._room_id

    async def get_live_handler(self) -> Observer:
        if self._live_handler is None:
            self._live_handler = Observer(room_id=(await self.get_room_id()))
        return self._live_handler

    async def _run(self):
        try:
            await self.bilibili_client.read_cookie()
            self._live_client = WSWebCookieLiveClient(
                room_id=await self.get_room_id(),
                bilibili_client=self.bilibili_client, bilibili_client_owner=False
            )
            live_handler = await self.get_live_handler()
            self._live_client.add_handler(live_handler)
            live_handler.start(self._live_client)
            await live_handler.astart(self._live_client)
            self._live_client.start()

            # polling dynamics in main
            last_got = set()
            while True:
                s = await self.bilibili_client.get_user_dynamic(self.uid)
                for item in s.items:
                    if item.id_str not in last_got:
                        rich.print(rf"\[{item.pub_date.strftime('%Y-%m-%d %H:%M:%S')}] "
                                   f"发布动态：{escape(item.text)}"
                                   f" [link {item.jump_url}]链接[/]")
                last_got = {item.id_str for item in s.items}
                await asyncio.sleep(self.dynamic_poll_interval)
        except asyncio.CancelledError:
            await self._live_client.stop()

    async def close(self):
        await self._live_client.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
