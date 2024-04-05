import asyncio
import random
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import patch, DEFAULT

import pytest
from pydantic import ValidationError, TypeAdapter

from ubw import models
from ubw.clients.testing import MockBilibiliClient, MockClient
from ubw.handlers.saver import SaverHandler, TimeDeltaSerializer
from ubw.testing.generate import generate_type


class MockAIOTinyDB:
    def __init__(self):
        self.queue = asyncio.Queue[list[tuple[str, Any]]]()
        self._actions: list[tuple[str, Any]] = []
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        actions = self._actions
        self._actions = []
        await self.queue.put(actions)
        self._lock.release()

    def insert(self, value):
        assert self._lock.locked()
        self._actions.append(('insert', value))


def test_time_delta_serializer():
    ser = TimeDeltaSerializer()
    assert ser.encode(timedelta(days=1, hours=1, minutes=1, seconds=1)) == '90061.0'
    assert ser.decode('90061') == timedelta(days=1, hours=1, minutes=1, seconds=1)


@pytest.mark.asyncio
async def test_saver():
    room_id = random.randrange(10000, 1000000)
    handler = SaverHandler(room_id=room_id)
    bilibili_client = MockBilibiliClient()
    client = MockClient(room_id=room_id)
    mock_db = MockAIOTinyDB()

    async with asyncio.timeout(5):
        with patch.multiple('ubw.handlers.saver',
                            datetime=DEFAULT,
                            AIOTinyDB=DEFAULT,
                            BilibiliUnauthorizedClient=DEFAULT) as p:
            p['datetime'].now.return_value = datetime.fromtimestamp(1)
            p['AIOTinyDB'].return_value = mock_db
            p['BilibiliUnauthorizedClient'].return_value = bilibili_client

            bilibili_client.__aenter__.return_value = bilibili_client

            def gibr(t):
                return generate_type(models.InfoByRoom, {
                    'room_info': {'room_id': room_id, 'live_start_time': t}})

            bilibili_client.get_info_by_room.side_effect = [
                gibr(0),
                gibr(1712308994),  # 2024-04-05T17:23:14+08:00
                gibr(0),
            ]
            handler.start(client)

            (a, s), = await mock_db.queue.get()
            assert bilibili_client.get_info_by_room.await_count == 1
            bilibili_client.get_info_by_room.assert_awaited_with(room_id)
            assert a == 'insert' and s['room_info']['room_id'] == room_id

            danmaku_command = generate_type(models.DanmakuCommand)
            await handler.on_danmu_msg(client, danmaku_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and s['info']['msg'] == danmaku_command.info.msg

            send_gift_command = generate_type(models.GiftCommand)
            await handler.on_send_gift(client, send_gift_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and s['data']['price'] == send_gift_command.data.price

            guard_buy_command = generate_type(models.GuardBuyCommand)
            await handler.on_guard_buy(client, guard_buy_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and s['data']['gift_name'] == guard_buy_command.data.gift_name

            super_chat_command = generate_type(models.SuperChatCommand)
            await handler.on_super_chat_message(client, super_chat_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and s['data']['message'] == super_chat_command.data.message

            room_change_command = generate_type(models.RoomChangeCommand)
            await handler.on_room_change(client, room_change_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and s['data']['title'] == room_change_command.data.title

            live_command = generate_type(models.LiveCommand)
            await handler.on_live(client, live_command)
            assert handler._wait_sharding.result() is None
            (a, s), = await mock_db.queue.get()
            assert bilibili_client.get_info_by_room.await_count == 2
            bilibili_client.get_info_by_room.assert_awaited_with(room_id)
            assert a == 'insert' and s['room_info']['room_id'] == room_id

            preparing_command = generate_type(models.PreparingCommand)
            await handler.on_preparing(client, preparing_command)
            assert handler._wait_sharding.result() is None
            (a, s), = await mock_db.queue.get()
            assert bilibili_client.get_info_by_room.await_count == 3
            bilibili_client.get_info_by_room.assert_awaited_with(room_id)
            assert a == 'insert' and s['room_info']['room_id'] == room_id

            room_block_command = generate_type(models.RoomBlockCommand)
            await handler.on_room_block_msg(client, room_block_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and room_block_command.data.uname == s['data']['uname']

            warning_command = generate_type(models.WarningCommand)
            await handler.on_warning(client, warning_command)
            (a, s), = await mock_db.queue.get()
            assert a == 'insert' and warning_command.msg == s['msg']

            unknown_cmd = {}
            try:
                TypeAdapter(models.AnnotatedCommandModel).validate_python(unknown_cmd)
            except ValidationError as e:
                err = e
            else:
                raise RuntimeError('ValidationError not raised')

            with patch('ubw.handlers._base.BaseHandler.on_unknown_cmd') as g:
                await handler.on_unknown_cmd(client, unknown_cmd, err)
                (a, s), = await mock_db.queue.get()
                assert a == 'insert' and s == {'UNKNOWN': True}
                g.assert_awaited_once_with(client, unknown_cmd, err)
