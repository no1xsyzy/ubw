import asyncio
from datetime import datetime
from functools import cached_property

from ._base import *
from ..ui import *


class ObserverHandler(BaseHandler):
    cls: Literal['observer'] = 'observer'
    room_id: int

    ui: UI = Richy()
    owned_ui: bool = True

    # states
    update_time: datetime | None = None
    title: str | None = None
    parent_area_name: str | None = None
    area_name: str | None = None
    living: bool | None = None
    ui_living_banner_key: str | None = None

    @cached_property
    def _banner_lock(self):
        return asyncio.Lock()

    async def _get_room_info(self, bclient) -> models.RoomInfo:
        return (await bclient.get_info_by_room(self.room_id)).room_info

    async def start(self, client):
        await super().start(client)
        if self.owned_ui:
            await self.ui.start()
        room_info = await self._get_room_info(client.bilibili_client)
        await self.change_state(
            title=room_info.title,
            parent_area_name=room_info.parent_area_name,
            area_name=room_info.area_name,
            living=(room_info.live_start_time is not None),
        )

    async def change_state(self, *, update_time=None, title=None, parent_area_name=None, area_name=None, living=None):
        if update_time is not None:
            self.update_time = update_time
        else:
            self.update_time = datetime.now()
        if title is not None:
            self.title = title
        if parent_area_name is not None:
            self.parent_area_name = parent_area_name
        if area_name is not None:
            self.area_name = area_name
        if living is not None:
            self.living = living

        assert (self.title is not None and
                self.parent_area_name is not None and self.area_name is not None
                and self.living is not None), "nothing changed"
        async with self._banner_lock:
            if self.ui_living_banner_key is not None:
                await self.ui.edit_record(self.ui_living_banner_key, sticky=False)
            self.ui_living_banner_key = await self.ui.add_record(Record(time=self.update_time, segments=[
                PlainText(text=f"[{self.room_id}] "),
                PlainText(text=f"\N{Ear}开始侦听，当前"),
                (PlainText(text=f"\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播中")
                 if living else
                 PlainText(text="\N{Black Square For Stop}\N{VS16}未直播")),
                PlainText(text="，标题"),
                RoomTitle(title=self.title, room_id=self.room_id),
                PlainText(text=f"，分区：{self.parent_area_name}/{self.area_name}")
            ]), sticky=True)

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        await self.ui.add_record(Record(time=message.ct, segments=[
            PlainText(text="直播间信息变更"),
            RoomTitle(title=title, room_id=self.room_id),
            PlainText(text=f"，分区：{parent_area_name}/{area_name}")
        ]))
        await self.change_state(update_time=message.ct, title=title,
                                parent_area_name=parent_area_name, area_name=area_name)

    async def on_live(self, client, message):
        await self.ui.add_record(Record(segments=[
            PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播开始"),
        ], time=message.ct))
        await self.change_state(update_time=message.ct, living=True)

    async def on_preparing(self, client, message):
        await self.ui.add_record(Record(segments=[
            PlainText(text="\N{Black Square For Stop}\N{VS16}直播结束"),
        ], time=message.ct))
        await self.change_state(update_time=message.ct, living=False)
