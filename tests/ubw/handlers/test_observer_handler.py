import re
from unittest.mock import patch

import pytest

from ubw.clients import MockClient
from ubw.handlers.observe import Observer
from ubw.models import InfoByRoom, RoomChangeCommand, PreparingCommand, LiveCommand


class TestObserve:
    @pytest.mark.asyncio
    async def test_observer_handler(self):
        room_id = 123

        handler = Observer(room_id=room_id)
        # bclient = MockBilibiliClient()
        client = MockClient(room_id=room_id, bilibili_client={})
        # client.bilibili_c/lient = bclient
        client.bilibili_client.get_info_by_room.return_value = InfoByRoom(
            room_info={'room_id': 1, 'short_id': 1, 'uid': 1, 'live_start_time': 0, 'title': "title", 'cover': "cover",
                       'area_id': 1, 'area_name': "area_name", 'parent_area_id': 1,
                       'parent_area_name': "parent_area_name", 'keyframe': "keyframe"},
            silent_room_info={'type': "type", 'level': 1, 'second': 1, 'expire_time': 1},
        )

        with patch('rich.print') as rp:
            await handler.start(client)
            client.bilibili_client.get_info_by_room.assert_awaited_once_with(room_id)
            rp.assert_called_once()
            call_args = rp.call_args
            assert call_args.kwargs == {}
            assert len(call_args.args) == 1
            assert re.match(
                r".+未直播.+分区：parent_area_name/area_name",
                call_args.args[0]
            )

    @pytest.mark.asyncio
    async def test_on_room_change(self):
        room_id = 123

        handler = Observer(room_id=room_id)
        client = MockClient(room_id=room_id)
        message = RoomChangeCommand(
            cmd='ROOM_CHANGE',
            data={
                'title': "title",
                'area_id': 1,
                'parent_area_id': 1,
                'area_name': "area_name",
                'parent_area_name': "parent_area_name",
                'live_key': "live_key",
                'sub_session_key': "sub_session_key",
            }
        )

        with patch('rich.print') as rp:
            await handler.on_room_change(client, message)
            rp.assert_called_once()
            call_args = rp.call_args
            assert call_args.kwargs == {}
            assert len(call_args.args) == 1
            assert re.match(
                r".+直播间信息变更.+title.+分区：parent_area_name/area_name",
                call_args.args[0]
            )

    @pytest.mark.asyncio
    async def test_on_live(self):
        room_id = 123

        handler = Observer(room_id=room_id)
        client = MockClient(room_id=room_id)
        message = LiveCommand(
            cmd='LIVE',
            live_key="live_key",
            voice_background="voice_background",
            sub_session_key="sub_session_key",
            live_platform="live_platform",
            live_model=0,
            live_time=None,
            roomid=room_id,
        )

        with patch('rich.print') as rp:
            await handler.on_live(client, message)

            rp.assert_called_once()
            call_args = rp.call_args
            assert call_args.kwargs == {}
            assert len(call_args.args) == 1
            assert re.match(
                r".+直播开始",
                call_args.args[0]
            )

    @pytest.mark.asyncio
    async def test_on_preparing(self):
        room_id = 123

        handler = Observer(room_id=room_id)
        client = MockClient(room_id=room_id)
        message = PreparingCommand(
            cmd='PREPARING',
            roomid=123,
            round=False,
        )

        with patch('rich.print') as rp:
            await handler.on_preparing(client, message)
            rp.assert_called_once()
            call_args = rp.call_args
            assert call_args.kwargs == {}
            assert len(call_args.args) == 1
            assert re.match(
                r".+直播结束",
                call_args.args[0]
            )
