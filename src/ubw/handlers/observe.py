import asyncio
from datetime import datetime, timedelta
from functools import cached_property

from ubw.clients import BilibiliClient
from ubw.push.qmsg import QMsgPusher
from ubw.push.serverchan import ServerChanPusher, ServerChanMessage
from ubw.ui.stream_view import *
from ._base import *


class ObserverHandler(BaseHandler):
    cls: Literal['observer'] = 'observer'
    room_id: int

    # low config
    live_push_throttle: timedelta = timedelta(minutes=30)

    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True
    ui: StreamView = Richy()
    owned_ui: bool = True
    server_chan: ServerChanPusher | None = None
    owned_server_chan: bool = True
    qmsg: QMsgPusher | None = None
    owned_qmsg: bool = True

    # states
    up_id: int | None = None
    up_name: str | None = None
    update_time: datetime | None = None
    title: str | None = None
    parent_area_name: str | None = None
    area_name: str | None = None
    living: bool | None = None
    ui_living_banner_key: str | None = None

    last_live_change: datetime | None = None

    @cached_property
    def _banner_lock(self):
        return asyncio.Lock()

    async def start(self, client):
        await super().start(client)
        if self.owned_ui:
            await self.ui.start()
        info_by_room: models.InfoByRoom = await self.bilibili_client.get_info_by_room(self.room_id)
        await self.change_state(
            up_id=info_by_room.room_info.uid,
            up_name=info_by_room.anchor_info.base_info.uname,
            title=info_by_room.room_info.title,
            parent_area_name=info_by_room.room_info.parent_area_name,
            area_name=info_by_room.room_info.area_name,
            living=(info_by_room.room_info.live_start_time is not None),
        )

    async def change_state(self, *,
                           up_id=None, up_name=None,
                           update_time=None, title=None, parent_area_name=None, area_name=None, living=None):
        push_marks = set()
        if up_id is not None:
            self.up_id = up_id
        if up_name is not None:
            self.up_name = up_name
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
            if self.living is False and living is True:
                push_marks.add('直播开始')
            else:
                push_marks.add('直播情况变更但不是开始')
            self.living = living

        assert (self.title is not None and
                self.parent_area_name is not None and self.area_name is not None
                and self.living is not None), "insufficient information!"
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
        await self.deal_with_push(push_marks)

    async def deal_with_push(self, push_marks):
        if '直播开始' in push_marks:
            if self.last_live_change is not None and datetime.now() - self.last_live_change <= self.live_push_throttle:
                return
            self.last_live_change = datetime.now()
            if self.server_chan is not None:
                await self.server_chan.push(ServerChanMessage(
                    title='直播开始',
                    desp=f"{self.up_name}开始直播了！"
                         "\n\n"
                         f"[点击观看《{self.title}》](bilibili://live/{self.room_id})"
                    ,
                ))
            if self.qmsg is not None:
                await self.qmsg.push(f"{self.up_name} 开始直播《{self.title}》")
        elif '直播情况变更但不是开始' in push_marks:
            self.last_live_change = datetime.now()

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

    async def close(self):
        if self.server_chan is not None and self.owned_server_chan:
            await self.server_chan.close()
        if self.qmsg is not None and self.owned_qmsg:
            await self.qmsg.close()
