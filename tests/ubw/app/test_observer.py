import asyncio
import dataclasses
from datetime import datetime
from unittest.mock import patch, AsyncMock

import pytest

from ubw.app import ObserverApp
from ubw.clients import MockBilibiliClient, WSWebCookieLiveClient
from ubw.handlers.observe import Observer
from ubw.testing.checkpoint import Checkpoint


@dataclasses.dataclass
class DynamicItem:
    id_str: str
    pub_date: datetime
    text: str
    jump_url: str


@dataclasses.dataclass
class OffsetList:
    items: list[DynamicItem]


@pytest.mark.asyncio
async def test_observer():
    bilibili_client = MockBilibiliClient()
    uid = 123
    room_id = 42

    bilibili_client.get_account_info.return_value.live_room_id = room_id

    app = ObserverApp(uid=uid, bilibili_client=bilibili_client, dynamic_poll_interval=1)

    checkpoint1 = Checkpoint()
    checkpoint2 = Checkpoint()
    checkpoint3 = Checkpoint()

    async def p():
        app.start()
        await app.join()

    t = 0

    def get_user_dynamic(arg):
        assert arg == uid
        nonlocal t
        t += 1
        if t == 1:
            checkpoint3.reach()
            return OffsetList(items=[
                DynamicItem(id_str='1', pub_date=datetime(1999, 12, 31, 23, 59, 59),
                            text='sample text', jump_url='url://fake')
            ])
        elif t == 2:
            raise asyncio.CancelledError

    bilibili_client.get_user_dynamic.side_effect = get_user_dynamic

    def read_cookie():
        checkpoint1.reach()

    bilibili_client.read_cookie.side_effect = read_cookie

    with patch('ubw.app.observer.Observer', spec=Observer) as patch_observer_handler_class:

        async def astart(c):
            checkpoint2.reach()
            assert c is app._live_client

        patch_observer_handler_class.return_value.astart.side_effect = astart
        with patch('ubw.app.observer.WSWebCookieLiveClient', spec=WSWebCookieLiveClient) as patch_live_client_class:
            async def g():
                raise asyncio.CancelledError

            patch_live_client_class.return_value.stop.return_value = g()
            with patch('rich.print') as patch_rich_print:
                task = asyncio.create_task(p())

                await checkpoint1
                bilibili_client.read_cookie.assert_awaited_once_with()

                await checkpoint2
                bilibili_client.get_account_info.assert_awaited_once_with(uid)
                patch_live_client_class.assert_called_once_with(
                    room_id=room_id,
                    bilibili_client=bilibili_client, bilibili_client_owner=False
                )
                patch_observer_handler_class.assert_called_once_with(room_id=room_id)
                live_client: AsyncMock = app._live_client  # noqa
                live_handler: AsyncMock = app._live_handler  # noqa
                live_client.add_handler.assert_called_once_with(live_handler)
                live_handler.start.assert_called_once_with(live_client)
                live_handler.astart.assert_awaited_once_with(live_client)

                await checkpoint3
                live_client.start.assert_called_once_with()

                with pytest.raises(asyncio.CancelledError):
                    await task
                live_client.stop.assert_called_once_with()
                patch_rich_print.assert_called_once_with(
                    r"\[1999-12-31 23:59:59] 发布动态：sample text [link url://fake]链接[/]")

                await app.close()
                live_client.close.assert_awaited_once_with()
