import asyncio
import random
from datetime import datetime, timedelta

from pydantic import Field
from typing_extensions import TypedDict

from ._base import *
from ..clients import BilibiliClient
from ..ui import *


class Info(TypedDict):
    up_id: int
    up_name: str
    title: str
    parent_area_name: str
    area_name: str
    living: bool

    update_time: datetime


class LivingStatusHandler(BaseHandler):
    # id
    cls: Literal['living_status'] = 'living_status'

    # high config
    interactive: bool = False

    # low config
    active_refresh_interval: timedelta = timedelta(seconds=60)

    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True
    ui: UI = Richy()
    owned_ui: bool = True

    # states
    info_cache: dict[int, Info] = Field(default_factory=dict)
    ui_keys: dict[int, str] = Field(default_factory=dict)

    # runtime
    _bilibili_client_started: bool = False
    _ui_started: bool = False
    _refresh_task: asyncio.Task | None = None

    async def ensure_info(self, room_id, force_update=False):
        if not force_update and room_id in self.info_cache:
            return False
        info: models.InfoByRoom = await self.bilibili_client.get_info_by_room(room_id)
        up_id = info.room_info.uid
        up_name = info.anchor_info.base_info.uname
        title = info.room_info.title
        parent_area_name = info.room_info.parent_area_name
        area_name = info.room_info.area_name
        living = info.room_info.live_start_time is not None
        if room_id not in self.info_cache:
            updated = True
        else:
            cached = self.info_cache[room_id]
            if (title != cached['title'] or parent_area_name != cached['parent_area_name'] or
                    area_name != cached['area_name'] or living != cached['living']):
                updated = True
            else:
                updated = False
        self.info_cache[room_id] = Info(
            up_id=up_id, up_name=up_name,
            title=title,
            parent_area_name=parent_area_name, area_name=area_name,
            living=living,
            update_time=datetime.now(),
        )
        return updated

    async def get_info(self, room_id, force_update=False) -> Info:
        if room_id not in self.info_cache:
            await self.ensure_info(room_id, force_update)
        return self.info_cache[room_id]

    async def start(self, client):
        room_id = client.room_id
        if self.bilibili_client_owner and not self._bilibili_client_started:
            await self.bilibili_client.__aenter__()
        if self.owned_ui and not self._ui_started:
            await self.ui.start()
        await self.refresh_record(room_id)
        self._refresh_task = asyncio.create_task(self.t_active_refresh())

    async def refresh_record(self, room_id):
        info = await self.get_info(room_id)
        record = self.make_record(room_id, info)
        if room_id in self.ui_keys:
            await self.ui.edit_record(self.ui_keys[room_id], record=record)
        else:
            self.ui_keys[room_id] = await self.ui.add_record(record, sticky=True)

    @staticmethod
    def make_record(room_id: int, info: Info):
        return Record(time=info['update_time'], segments=[
            PlainText(text=f"[{room_id}] "),
            PlainText(text=f"\N{Ear}开始侦听，当前"),
            (PlainText(text=f"\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播中")
             if info['living'] else
             PlainText(text="\N{Black Square For Stop}\N{VS16}未直播")),
            PlainText(text="，标题"),
            RoomTitle(title=info['title'], room_id=room_id),
            PlainText(text=f"，分区：{info['parent_area_name']}/{info['area_name']}")
        ])

    async def t_active_refresh(self):
        while True:
            await asyncio.sleep(self.active_refresh_interval.total_seconds())
            to_refresh = random.choice(list(self.info_cache.keys()))
            await self.ensure_info(to_refresh)

    async def on_room_change(self, client, message):
        room_id = client.room_id
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        self.info_cache[room_id].update(title=title, parent_area_name=parent_area_name, area_name=area_name)
        await self.refresh_record(room_id)

    async def on_live(self, client, message):
        room_id = client.room_id
        self.info_cache[room_id]['living'] = True
        await self.refresh_record(room_id)

    async def on_preparing(self, client, message):
        room_id = client.room_id
        self.info_cache[room_id]['living'] = False
        await self.refresh_record(room_id)
