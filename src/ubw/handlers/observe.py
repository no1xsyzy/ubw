from datetime import datetime

import rich
from rich.markup import escape

from ._base import *
from .. import models


class Observer(BaseHandler):
    cls: Literal['observer'] = 'observer'
    room_id: int

    async def get_room_info(self, bclient) -> models.RoomInfo:
        return (await bclient.get_info_by_room(self.room_id)).room_info

    async def astart(self, client):
        now = datetime.now()
        room_id = client.room_id
        room_info = await self.get_room_info(client.bilibili_client)
        title = room_info.title
        parent_area_name = room_info.parent_area_name
        area_name = room_info.area_name
        living = room_info.live_start_time is not None
        rich.print(
            rf"\[{now.strftime('%Y-%m-%d %H:%M:%S')}] "
            rf"\[[bright_cyan]{room_id}[/]] "
            f":ear-text:开始侦听，当前"
            + ("[bright_green]直播中[/]" if living else "未直播") +
            f"，标题《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}"
        )

    async def on_room_change(self, client, message):
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_live(self, client, message):
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            ":black_right__pointing_triangle_with_double_vertical_bar-text:直播开始")

    async def on_preparing(self, client, message):
        rich.print(
            rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
            ":black_square_for_stop-text:直播结束")
