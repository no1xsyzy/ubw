import asyncio
import os
import re
import sys
import typing
from datetime import timedelta
from operator import itemgetter
from typing import Literal

import attr
from bilibili_api.video import Video
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Footer, Header, Markdown, Button, Digits, Label

from ubw import models
from ubw.clients import LiveClientABC, BilibiliClient
from ubw.handlers import BaseHandler

owner = itemgetter('name', 'mid', 'face')

DEBUG_VODT = os.environ.get('DEBUG_VODT')

FORMAT_TEXT = (
    """[{demander_uname}](https://space.bilibili.com/{demander_uid})"""
    """点播了"""
    """[《{title}》({bvid})](https://www.bilibili.com/video/{bvid}/)"""
    """（作者：[{owner_uname}](https://space.bilibili.com/{owner_uid})）"""
    """时长：{duration}"""
)


def exit_with_task(fut: asyncio.Task | asyncio.Future):
    sys.exit(fut.cancelled() or fut.exception() is not None)


@attr.define
class VodInfo:
    bvid: str
    duration: timedelta
    title: str
    demander_uname: str
    demander_uid: int
    demander_face: str
    owner_uname: str
    owner_uid: int
    owner_face: str


class UI(App):
    CSS_PATH = "vodt.tcss"
    TITLE = "点播机"

    if typing.TYPE_CHECKING:
        queue: list[VodInfo]
    else:
        queue: reactive[list[VodInfo]] = reactive(list, recompose=True)

    @property
    def total_time(self):
        return sum((e.duration for e in self.queue), timedelta())

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

        yield HorizontalGroup(Label("总时长"), Digits(str(self.total_time)))

        group = (HorizontalGroup(
            Markdown(FORMAT_TEXT.format_map(attr.asdict(it))),
            Button("删除", id=f"remove_{it.bvid}")
        ) for it in self.queue)
        yield VerticalScroll(*group, id="scroll")

    def add_item(self, vod_info: VodInfo):
        self.queue.append(vod_info)
        self.mutate_reactive(UI.queue)

    def remove_item(self, bvid: str):
        try:
            to_remove = next(item for item in self.queue if item.bvid == bvid)
        except StopIteration:
            return
        self.queue.remove(to_remove)
        self.mutate_reactive(UI.queue)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id.split("_"):
            case ['remove', bvid]:
                self.remove_item(bvid)

    def on_mount(self):
        if DEBUG_VODT:
            self._some_task = asyncio.create_task(self.appender())

    async def appender(self):
        demander = "橘枳橼", 2351778, "https://i2.hdslb.com/bfs/garb/open/7bfb44777ed5882f125a484ed6f2e3599a7c55c3.png"
        up = "暗视者ShadowVisual", 13583619, "https://i2.hdslb.com/bfs/face/a29503c5c118512aba752fe30b22f4b5b8b610d3.jpg"
        from itertools import count
        for i in count():
            await asyncio.sleep(0 if i < 4 else 1 if i < 10 else 20)
            self.add_item(VodInfo(f'BV{i}', timedelta(seconds=120 * 2 ** i), f"title_{i}", *demander, *up))


class VodTextualHandler(BaseHandler):
    cls: Literal['vodt'] = 'vodt'

    _ui_task: asyncio.Task | None = None

    _ui: UI

    async def start(self, client: LiveClientABC):
        self._ui = UI()
        self._ui_task = asyncio.create_task(self._ui.run_async())
        self._ui_task.add_done_callback(exit_with_task)

    async def on_super_chat_message(self, client: LiveClientABC, message: models.SuperChatCommand):
        bclient: BilibiliClient = client.bilibili_client
        for bvid in re.findall(r"BV\w{10}", message.data.message):
            detail = await Video(bvid, await bclient.get_credential()).get_detail()
            duration = timedelta(seconds=detail['View']['duration'])
            title = detail['View']['title']
            demander_uname = message.data.user_info.uname
            demander_uid = message.data.uid
            demander_face = message.data.user_info.face
            owner_uname, owner_uid, owner_face = owner(detail['View']['owner'])
            self._ui.add_item(
                VodInfo(bvid=bvid, duration=duration, title=title,
                        demander_uname=demander_uname, demander_uid=demander_uid, demander_face=demander_face,
                        owner_uname=owner_uname, owner_uid=owner_uid, owner_face=owner_face))


async def main():
    global DEBUG_VODT
    DEBUG_VODT = "1"
    ui = UI()

    await ui.run_async()


if __name__ == '__main__':
    asyncio.run(main())
