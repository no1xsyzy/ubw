import asyncio
from datetime import datetime

import pytest

from ubw.clients import BilibiliUnauthorizedClient
from ubw.handlers.observe import ObserverHandler
from ubw.models import InfoByRoom, RoomChangeCommand, LiveCommand, PreparingCommand
from ubw.push.serverchan import ServerChanPusher
from ubw.testing.asyncstory import AsyncStoryline, AsyncMock
from ubw.testing.generate import generate_type, generate_random_string
from ubw.ui.stream_view import RoomTitle, Richy


class ASMockBC(AsyncMock):
    def make_session(self):
        return self.session

    @property
    def auth_type(self):
        return 'no'

    @property
    def __class__(self):
        return BilibiliUnauthorizedClient


class MockUI(AsyncMock):
    @property
    def uic(self):
        return 'richy'

    @property
    def __class__(self):
        return Richy


@pytest.mark.asyncio
async def test_observer_handler():
    async with asyncio.timeout(5):
        with AsyncStoryline() as liv:
            room_id = 123
            title = generate_random_string('title')
            title2 = generate_random_string('title2')
            parent_area_name = generate_random_string('parent_area_name')
            area_name = generate_random_string('area_name')

            ui = liv.add_async_mock(mock_class=MockUI)
            client = liv.add_async_mock()
            bilibili_client = liv.add_async_mock(mock_class=ASMockBC)
            server_chan = liv.add_async_mock(mimics=ServerChanPusher)

            handler = ObserverHandler(room_id=room_id, ui=ui, server_chan=server_chan, bilibili_client=bilibili_client)

            # start
            t = asyncio.create_task(handler.start(client))
            c = await liv.get_call(target=ui.start, f='async')
            c.assert_match_call()
            c.set_result(None)
            c = await liv.get_call(target=bilibili_client.get_info_by_room, f='async')
            c.assert_match_call(123)
            c.set_result(generate_type(InfoByRoom, {
                'room_info': {
                    'title': title,
                    'parent_area_name': parent_area_name,
                    'area_name': area_name,
                    'live_start_time': None,
                }
            }))
            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[0].text == f"[{room_id}] "
            assert "未直播" in c.args[0].segments[2].text
            assert c.args[0].segments[4] == RoomTitle(title=title, room_id=room_id)
            assert c.args[0].segments[5].text == f"，分区：{parent_area_name}/{area_name}"
            assert c.kwargs == {'sticky': True}
            c.set_result('a')
            await t

            # room change
            t = asyncio.create_task(handler.on_room_change(client, generate_type(RoomChangeCommand, {
                'data': {
                    'title': title2,
                    'parent_area_name': parent_area_name,
                    'area_name': area_name,
                },
                'ct': datetime.now(),
            })))
            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[0].text == "直播间信息变更"
            assert c.args[0].segments[1].title == title2
            c.set_result(None)
            c = await liv.get_call(target=ui.edit_record, f='async')
            c.assert_match_call('a', sticky=False)
            c.set_result(None)
            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[4] == RoomTitle(title=title2, room_id=room_id)
            assert c.kwargs == {'sticky': True}
            c.set_result('b')
            await t

            # live
            t = asyncio.create_task(handler.on_live(client, generate_type(LiveCommand)))
            c = await liv.get_call(target=ui.add_record, f='async')
            assert "直播开始" in c.args[0].segments[0].text
            c.set_result(None)
            c = await liv.get_call(target=ui.edit_record, f='async')
            c.assert_match_call('b', sticky=False)
            c.set_result(None)
            c = await liv.get_call(target=ui.add_record, f='async')
            assert "直播中" in c.args[0].segments[2].text
            assert c.kwargs == {'sticky': True}
            c.set_result('c')
            await t

            # preparing
            t = asyncio.create_task(handler.on_preparing(client, generate_type(PreparingCommand)))
            c = await liv.get_call(target=ui.add_record, f='async')
            assert "直播结束" in c.args[0].segments[0].text
            c.set_result(None)
            c = await liv.get_call(target=ui.edit_record, f='async')
            c.assert_match_call('c', sticky=False)
            c.set_result(None)
            c = await liv.get_call(target=ui.add_record, f='async')
            assert "未直播" in c.args[0].segments[2].text
            assert c.kwargs == {'sticky': True}
            c.set_result('d')
            await t
