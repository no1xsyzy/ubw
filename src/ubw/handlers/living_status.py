import asyncio
import random
from datetime import datetime, timedelta

from pydantic import Field, BaseModel

from ._base import *
from ..clients import BilibiliClient
from ..ui import *


class Info(BaseModel):
    up_id: int
    up_name: str
    up_face: str
    title: str
    parent_area_name: str
    area_name: str
    living: bool
    key_frame: str
    cover: str

    @classmethod
    def from_info_by_room(cls, info_by_room: models.InfoByRoom):
        return cls(
            up_id=info_by_room.room_info.uid,
            up_name=info_by_room.anchor_info.base_info.uname,
            up_face=info_by_room.anchor_info.base_info.face,
            title=info_by_room.room_info.title,
            parent_area_name=info_by_room.room_info.parent_area_name,
            area_name=info_by_room.room_info.area_name,
            living=info_by_room.room_info.live_start_time is not None,
            key_frame=info_by_room.room_info.keyframe,
            cover=info_by_room.room_info.cover,
        )


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
    update_time: dict[int, datetime] = Field(default_factory=dict)
    ui_keys: dict[int, str] = Field(default_factory=dict)

    # runtime
    _bilibili_client_started: bool = False
    _ui_started: bool = False
    _refresh_task: asyncio.Task | None = None

    async def join(self):
        await asyncio.gather(super().join(), self._refresh_task)

    async def ensure_info(self, room_id, *, force_update=False) -> tuple[Info, datetime]:
        if not force_update and room_id in self.info_cache:
            return self.info_cache[room_id], self.update_time[room_id]
        info = await self.bilibili_client.get_info_by_room(room_id)
        new = Info.from_info_by_room(info)
        update_time = datetime.now()
        self.update_time[room_id] = update_time
        self.info_cache[room_id] = new
        return new, update_time

    def update_info(self, room_id, /, **update):
        self.info_cache[room_id] = self.info_cache[room_id].model_copy(update=update)
        self.update_time[room_id] = datetime.now()

    async def start(self, client):
        room_id = client.room_id
        if self.bilibili_client_owner and not self._bilibili_client_started:
            await self.bilibili_client.__aenter__()
            self._bilibili_client_started = True
        if self.owned_ui and not self._ui_started:
            await self.ui.start()
            self._ui_started = True
        await self.refresh_record(room_id)
        if self._refresh_task is None:
            self._refresh_task = asyncio.create_task(self.t_active_refresh())

    async def stop(self):
        task = self._refresh_task
        self._refresh_task = None
        task.cancel('stop')
        try:
            await task
        except asyncio.CancelledError:
            pass

        await super().stop()

        if self.bilibili_client_owner and self._bilibili_client_started:
            await self.bilibili_client.stop()
            self._bilibili_client_started = False
        if self.owned_ui and self._ui_started:
            await self.ui.stop()
            self._ui_started = False

    async def refresh_record(self, room_id, *, force_update=False):
        info, time = await self.ensure_info(room_id, force_update=force_update)
        record = self.make_record(room_id, info, time)
        if room_id in self.ui_keys:
            await self.ui.edit_record(self.ui_keys[room_id], record=record)
        else:
            self.ui_keys[room_id] = await self.ui.add_record(record, sticky=True)

    @staticmethod
    def make_record(room_id: int, info: Info, time: datetime):
        if info.living:
            return Record(time=time, segments=[
                PlainText(text=f"[{room_id}] "),
                PlainText(text=f"\N{Ear}开始侦听，当前"),
                User(name=info.up_name, uid=info.up_id, face=info.up_face),
                PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播中"),
                PlainText(text="，标题"),
                RoomTitle(title=info.title, room_id=room_id),
                PlainText(text=f"，分区：{info.parent_area_name}/{info.area_name}"),
                LineBreak(),
                Picture(url=info.cover, alt="封面图"),
                Picture(url=info.key_frame, alt="关键帧"),
            ], importance=20)
        else:
            return Record(time=time, segments=[
                PlainText(text=f"[{room_id}] "),
                PlainText(text=f"\N{Ear}开始侦听，当前"),
                User(name=info.up_name, uid=info.up_id, face=info.up_face),
                PlainText(text="\N{Black Square For Stop}\N{VS16}未直播"),
                PlainText(text="，标题"),
                RoomTitle(title=info.title, room_id=room_id),
                PlainText(text=f"，分区：{info.parent_area_name}/{info.area_name}")
            ])

    async def t_active_refresh(self):
        while True:
            await asyncio.sleep(self.active_refresh_interval.total_seconds())
            to_refresh = random.choice(list(self.info_cache.keys()))
            await self.refresh_record(to_refresh, force_update=True)

    async def on_room_change(self, client, message):
        room_id = client.room_id
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        self.update_info(room_id, title=title, parent_area_name=parent_area_name, area_name=area_name)
        await self.refresh_record(room_id)

    async def on_live(self, client, message):
        room_id = client.room_id
        self.update_info(room_id, living=True)
        await self.refresh_record(room_id)

    async def on_preparing(self, client, message):
        room_id = client.room_id
        self.update_info(room_id, living=False)
        await self.refresh_record(room_id)
