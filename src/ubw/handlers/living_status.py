from datetime import datetime
from functools import cached_property

from ._base import *


class LivingStatusHandler(BaseHandler):
    cls: Literal['living_status'] = 'living_status'
    interactive: bool = False

    @cached_property
    def _info_by_room_cache(self):
        return {}

    async def info_by_room(self, room_id, bclient):
        if room_id not in self._info_by_room_cache:
            info: models.InfoByRoom = await bclient.get_info_by_room(room_id)
            title = info.room_info.title
            parent_area_name = info.room_info.parent_area_name
            area_name = info.room_info.area_name
            living = info.room_info.live_start_time is not None
            self._info_by_room_cache[room_id] = [title, parent_area_name, area_name, living]
        return self._info_by_room_cache[room_id]

    async def astart(self, client):
        now = datetime.now()
        room_id = client.room_id
        title, parent_area_name, area_name, living = await self.info_by_room(room_id, client.bilibili_client)
        rich.print(
            rf"\[{now.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            f":ear-text:开始侦听，当前"
            + ("[bright_green]直播中[/]" if living else "未直播") +
            f"，标题《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}"
        )

    async def on_room_change(self, client, message):
        room_id = client.room_id
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name

        self._info_by_room_cache[room_id][0:3] = title, parent_area_name, area_name

        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_live(self, client, message):
        room_id = client.room_id
        self._info_by_room_cache[room_id][3] = True
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            ":black_right__pointing_triangle_with_double_vertical_bar-text:直播开始")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        self._info_by_room_cache[room_id][3] = False
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] :black_square_for_stop-text:直播结束")
