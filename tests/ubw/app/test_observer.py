from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest
from pydantic import BaseModel

from ubw import models
from ubw.app import ObserverApp
from ubw.clients import BilibiliApiError, BilibiliUnauthorizedClient
from ubw.push.serverchan import ServerChanPusher
from ubw.testing.asyncstory import AsyncStoryline, AsyncMock, returns
from ubw.testing.generate import generate_type
from ubw.ui.stream_view import Richy


class ASMockBC2(AsyncMock):
    def make_session(self):
        return self.session

    @property
    def auth_type(self):
        return 'no'

    @property
    def __class__(self):
        return BilibiliUnauthorizedClient


class DynamicItem(BaseModel):
    id_str: str
    pub_date: datetime
    text: str
    jump_url: str

    is_topped: bool = False
    is_video: bool = False
    is_live: bool = False

    is_forward: bool = False
    orig: DynamicItem | None = None

    markdown: str = ""


class OffsetList(BaseModel):
    items: list[DynamicItem]


@pytest.mark.asyncio
async def test_observer():
    async with asyncio.timeout(5):
        with AsyncStoryline() as liv:
            uid = 123
            room_id = 42

            bilibili_client = liv.add_async_mock(mock_class=ASMockBC2)
            handler = liv.add_async_mock()
            client = liv.add_async_mock()
            ui = liv.add_async_mock(attrs={'uic': 'richy'}, mimics=Richy)
            server_chan = liv.add_async_mock(mimics=ServerChanPusher)

            client.add_handler = liv.add_sync_mock()(returns())

            handler_class = liv.add_sync_patch('ubw.app.observer.ObserverHandler')(returns(handler))
            client_class = liv.add_sync_patch('ubw.app.observer.WSWebCookieLiveClient')(returns(client))
            logger_exception = liv.add_sync_patch('ubw.app.observer.logger.exception')(returns(client))

            ass = liv.add_async_patch('asyncio.sleep')

            app = ObserverApp(
                uid=uid,
                bilibili_client=bilibili_client,
                ui=ui,
                server_chan=server_chan,
                dynamic_poll_interval=1,
            )

            await app.start()

            c = await liv.get_call(target=bilibili_client.read_cookie, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=ui.start, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=bilibili_client.get_account_info, f='async')
            c.assert_match_call(uid)
            c.set_result(generate_type(models.AccountInfo, {'live_room_id': room_id}))

            c = await liv.get_call(target=client_class, f='sync')
            c.assert_match_call(room_id=room_id, bilibili_client=bilibili_client, bilibili_client_owner=False)

            c = await liv.get_call(target=handler_class, f='sync')
            c.assert_match_call(
                room_id=room_id, ui=ui, owned_ui=False,
                bilibili_client=bilibili_client, bilibili_client_owner=False,
                server_chan=server_chan, owned_server_chan=False,
            )

            c = await liv.get_call(target=client.add_handler, f='sync')
            c.assert_match_call(handler)

            c = await liv.get_call(target=handler.start, f='async')
            c.assert_match_call(client)
            c.set_result(None)

            c = await liv.get_call(target=client.start, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=bilibili_client.get_user_dynamic, f='async')
            c.assert_match_call(uid)
            c.set_result(OffsetList(items=[
                DynamicItem(id_str='1', pub_date=datetime(1999, 12, 31, 23, 59, 59).astimezone(),
                            text='TEXT=1', jump_url='url://1', is_topped=True),
                DynamicItem(id_str='2', pub_date=datetime.now().astimezone() - timedelta(days=2, hours=1),
                            text='TEXT=2', jump_url='url://2'),
                DynamicItem(id_str='3', pub_date=datetime.now().astimezone() - timedelta(days=2, hours=-1),
                            text='TEXT=3', jump_url='url://3'),
            ]))

            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[0].text == "置顶动态"
            assert c.args[0].segments[0].href == "url://1"
            assert c.args[0].segments[1].text == " "
            assert c.args[0].segments[2].text == "TEXT=1"
            assert c.args[0].time == datetime(1999, 12, 31, 23, 59, 59).astimezone()
            c.set_result(None)

            try:
                c = await liv.get_call(target=ui.add_record, f='async')
            except asyncio.CancelledError:
                print(app._task.get_coro())
                raise

            assert c.args[0].segments[0].text == "发布动态"
            assert c.args[0].segments[0].href == "url://3"
            assert c.args[0].segments[1].text == " "
            assert c.args[0].segments[2].text == "TEXT=3"
            c.set_result(None)

            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[0].text == " ===== 以上为历史消息 ===== "
            c.set_result(None)

            c = await liv.get_call(target=ass, f='async')
            c.assert_match_call(1)
            c.set_result(None)

            c = await liv.get_call(target=bilibili_client.get_user_dynamic, f='async')
            c.assert_match_call(uid)
            c.set_result(OffsetList(items=[
                DynamicItem(id_str='3', pub_date=datetime.now().astimezone() - timedelta(days=2, hours=-1),
                            text='TEXT=3', jump_url='url://3'),
                DynamicItem(id_str='4', pub_date=datetime.now().astimezone() - timedelta(hours=1),
                            text='TEXT=4', jump_url='url://4', markdown='markdown4'),
            ]))

            c = await liv.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[0].text == "发布动态"
            assert c.args[0].segments[0].href == "url://4"
            assert c.args[0].segments[1].text == " "
            assert c.args[0].segments[2].text == "TEXT=4"
            c.set_result(None)

            c = await liv.get_call(target=server_chan.push, f='async')
            assert c.args[0].title == '发布动态'
            assert c.args[0].desp == 'markdown4'
            c.set_result(None)

            c = await liv.get_call(target=ass, f='async')
            c.assert_match_call(1)
            c.set_result(None)

            # if api raises error, log and continue
            e = BilibiliApiError("error")
            c = await liv.get_call(target=bilibili_client.get_user_dynamic, f='async')
            c.assert_match_call(uid)
            c.set_exception(e)
            c = await liv.get_call(target=logger_exception, f='sync')
            c.assert_match_call("exception in _fetch_print_update", exc_info=e)

            t = asyncio.create_task(app.stop())

            c = await liv.get_call(target=client.stop, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=handler.stop, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=ui.stop, f='async')
            c.assert_match_call()
            c.set_result(None)

            await t

            t = asyncio.create_task(app.close())

            c = await liv.get_call(target=client.close, f='async')
            c.assert_match_call()
            c.set_result(None)

            c = await liv.get_call(target=bilibili_client.close, f='async')
            c.assert_match_call()
            c.set_result(None)

            await t
