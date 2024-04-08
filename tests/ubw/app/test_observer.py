import asyncio
import dataclasses
import re
from datetime import datetime, timedelta

import pytest

from ubw import models
from ubw.app import ObserverApp
from ubw.clients import BilibiliUnauthorizedClient
from ubw.testing.asyncstory import AsyncStoryline, AsyncMock, returns
from ubw.testing.generate import generate_type


class ASMockBC2(AsyncMock):
    def make_session(self):
        return self.session

    @property
    def auth_type(self):
        return 'no'

    @property
    def __class__(self):
        return BilibiliUnauthorizedClient


@dataclasses.dataclass
class DynamicItem:
    id_str: str
    pub_date: datetime
    text: str
    jump_url: str
    is_topped: bool


@dataclasses.dataclass
class OffsetList:
    items: list[DynamicItem]


@pytest.mark.asyncio
async def test_observer():
    with AsyncStoryline() as liv:
        uid = 123
        room_id = 42
        bilibili_client = liv.add_async_mock(mock_class=ASMockBC2)

        handler = liv.add_async_mock()
        client = liv.add_async_mock()

        handler.start = liv.add_sync_mock()(returns())
        client.add_handler = liv.add_sync_mock()(returns())
        client.start = liv.add_sync_mock()(returns())

        handler_class = liv.add_sync_patch('ubw.app.observer.Observer')(returns(handler))
        client_class = liv.add_sync_patch('ubw.app.observer.WSWebCookieLiveClient')(returns(client))

        rp = liv.add_sync_patch('rich.print')(returns())
        ass = liv.add_async_patch('asyncio.sleep')

        app = ObserverApp(uid=uid, bilibili_client=bilibili_client, dynamic_poll_interval=1)

        app.start()

        c = await liv.get_call(target=bilibili_client.read_cookie, f='async')
        c.assert_match_call()
        c.set_result(None)

        c = await liv.get_call(target=bilibili_client.get_account_info, f='async')
        c.assert_match_call(uid)
        c.set_result(generate_type(models.AccountInfo, {'live_room_id': room_id}))

        c = await liv.get_call(target=client_class, f='sync')
        c.assert_match_call(room_id=room_id, bilibili_client=bilibili_client, bilibili_client_owner=False)

        c = await liv.get_call(target=handler_class, f='sync')
        c.assert_match_call(room_id=room_id)

        c = await liv.get_call(target=client.add_handler, f='sync')
        c.assert_match_call(handler)

        c = await liv.get_call(target=handler.start, f='sync')
        c.assert_match_call(client)

        c = await liv.get_call(target=handler.astart, f='async')
        c.assert_match_call(client)
        c.set_result(None)

        c = await liv.get_call(target=client.start, f='sync')
        c.assert_match_call()

        c = await liv.get_call(target=bilibili_client.get_user_dynamic, f='async')
        c.assert_match_call(uid)
        c.set_result(OffsetList(items=[
            DynamicItem(id_str='1', pub_date=datetime(1999, 12, 31, 23, 59, 59),
                        text='TEXT=1', jump_url='url://1', is_topped=True),
            DynamicItem(id_str='2', pub_date=datetime.now() - timedelta(days=2, hours=1),
                        text='TEXT=2', jump_url='url://2', is_topped=False),
            DynamicItem(id_str='3', pub_date=datetime.now() - timedelta(days=2, hours=-1),
                        text='TEXT=3', jump_url='url://3', is_topped=False),
        ]))

        c = await liv.get_call(target=rp, f='sync')
        c.assert_match_call(r"\[1999-12-31 23:59:59] [bright_blue]置顶动态[/]：TEXT=1 [link url://1]链接[/]")

        c = await liv.get_call(target=rp, f='sync', _debug=True)
        c.assert_complex_match(
            re.compile(r"\\\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d] 发布动态：TEXT=3 \[link url://3]链接\[/]$").match
        )

        c = await liv.get_call(target=rp, f='sync')
        c.assert_match_call(" ===== 以上为历史消息 ===== ")

        c = await liv.get_call(target=ass, f='async')
        c.assert_match_call(1)
        c.set_result(None)

        c = await liv.get_call(target=bilibili_client.get_user_dynamic, f='async')
        c.assert_match_call(uid)
        c.set_result(OffsetList(items=[
            DynamicItem(id_str='3', pub_date=datetime.now() - timedelta(days=2, hours=-1),
                        text='TEXT=3', jump_url='url://3', is_topped=False),
            DynamicItem(id_str='4', pub_date=datetime.now() - timedelta(hours=1),
                        text='TEXT=4', jump_url='url://4', is_topped=False),
        ]))

        c = await liv.get_call(target=rp, f='sync')
        c.assert_complex_match(
            re.compile(r"\\\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d] 发布动态：TEXT=4 \[link url://4]链接\[/]$").match
        )

        stop = app.stop()

        c = await liv.get_call(target=client.stop, f='async')
        c.assert_match_call()
        c.set_exception(asyncio.CancelledError)

        with pytest.raises(asyncio.CancelledError):
            await stop

        t = asyncio.create_task(app.close())

        c = await liv.get_call(target=client.close, f='async')
        c.assert_match_call()
        c.set_result(None)

        c = await liv.get_call(target=bilibili_client.close, f='async')
        c.assert_match_call()
        c.set_result(None)

        await t
