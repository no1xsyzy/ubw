import asyncio
import json
import random
from pathlib import Path

import pytest
from pydantic import ValidationError

from ubw import models
from ubw.handlers import DanmakuPHandler
from ubw.testing.asyncstory import AsyncStoryline, AsyncMock
from ubw.testing.generate import generate_type
from ubw.ui import Richy, User, RoomTitle, Currency, PlainText


class MockUI(AsyncMock):
    @property
    def uic(self):
        return 'richy'

    @property
    def __class__(self):
        return Richy


@pytest.mark.asyncio
async def test_danmakup():
    async with asyncio.timeout(5):
        with AsyncStoryline() as asl:
            room_id = random.randrange(10000, 100000)
            ui = asl.add_async_mock(mock_class=MockUI)
            client = asl.add_async_mock()
            client.room_id = room_id

            handler = DanmakuPHandler(ui=ui, ignore_danmaku='^ignore this$')

            t = asyncio.create_task(handler.start(client))
            c = await asl.get_call(target=ui.start, f='async')
            c.assert_match_call()
            c.set_result(None)
            await t

            # fully ignore ignore_danmaku specified pattern
            t = asyncio.create_task(handler.on_danmu_msg(client, generate_type(models.DanmakuCommand, {
                'info': {'msg': "ignore this"}
            })))
            # no ui.add_record call at all
            await t

            # trivial_rate very low for KAOMOJIS
            t = asyncio.create_task(handler.on_danmu_msg(client, generate_type(models.DanmakuCommand, {
                'info': {
                    'msg': "(⌒▽⌒)",
                }
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[1], User)
            assert c.args[0].segments[2].text == ": "
            assert c.args[0].importance == 0
            c.set_result(None)
            await t

            # info.mode_info.extra.emots
            t = asyncio.create_task(handler.on_danmu_msg(client, generate_type(models.DanmakuCommand, {
                'info': {
                    'msg': "[dog]",
                    'mode_info': {'extra': {'emots': {'[dog]': {}}}},
                }
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[1], User)
            assert c.args[0].segments[2].text == ": "
            assert c.args[0].importance == 0
            c.set_result(None)
            await t

            # info.mode_info.extra.emoticon_unique
            with open(Path(__file__).parent / 'danmu_msg_emoticon_unique.json', encoding='utf-8') as f:
                command = json.load(f)
            t = asyncio.create_task(handler.handle(client, command))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[1], User)
            assert c.args[0].segments[2].text == ": "
            assert c.args[0].importance == 0
            c.set_result(None)
            await t

            # normal text
            t = asyncio.create_task(handler.on_danmu_msg(client, generate_type(models.DanmakuCommand, {
                'info': {
                    'msg': "你好",
                    'mode_info': {'user': {'base': {'face': 'face'}}},
                }
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[1], User)
            assert c.args[0].segments[1].face == 'face'
            assert c.args[0].segments[2].text == "说: "
            assert c.args[0].importance == 10
            c.set_result(None)
            await t

            command = generate_type(models.GuardBuyCommand, {})
            async with asl.in_task(handler.on_summary(client, command.summarize())):
                c = await asl.get_call(target=ui.add_record, f='async')
                assert c.args[0].segments[3] == PlainText(text=" (GUARD_BUY)")
                c.set_result(None)

            t = asyncio.create_task(handler.on_room_change(client, generate_type(models.RoomChangeCommand, {})))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[2], RoomTitle)
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_warning(client, generate_type(models.WarningCommand)))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert '受到警告' in c.args[0].segments[1].text
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_super_chat_message(client, generate_type(models.SuperChatCommand)))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert isinstance(c.args[0].segments[3], Currency)
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_room_block_msg(client, generate_type(models.RoomBlockCommand)))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert c.args[0].segments[1].text == "用户被封禁"
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_live(client, generate_type(models.LiveCommand)))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert "直播开始" in c.args[0].segments[1].text
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_preparing(client, generate_type(models.PreparingCommand)))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert "直播结束" in c.args[0].segments[1].text
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_interact_word(client, generate_type(models.InteractWordCommand, {
                'data': {'msg_type': 1}
            })))
            await t

            await (handler.on_x_ubw_heartbeat(client, generate_type(models.XHeartbeatCommand)))

            t = asyncio.create_task(handler.on_send_gift(client, generate_type(models.GiftCommand, {
                'data': {'price': 0, 'coin_type': 'silver'}
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert len(c.args[0].segments) == 3
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_send_gift(client, generate_type(models.GiftCommand, {
                'data': {'price': 0, 'coin_type': 'gold'}
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert len(c.args[0].segments) == 4
            assert c.args[0].segments[3].price == 0
            c.set_result(None)
            await t

            t = asyncio.create_task(handler.on_send_gift(client, generate_type(models.GiftCommand, {
                'data': {'price': 10 * 1000, 'num': 20, 'coin_type': 'gold'}
            })))
            c = await asl.get_call(target=ui.add_record, f='async')
            assert len(c.args[0].segments) == 4
            assert c.args[0].segments[3].price == 200
            c.set_result(None)
            await t


@pytest.mark.asyncio
async def test_interact_word():
    with AsyncStoryline() as asl:
        ui = asl.add_async_mock(mock_class=MockUI)
        client = asl.add_async_mock()

        handler = DanmakuPHandler(ui=ui, gift_threshold=10, show_interact_word=True)

        t = asyncio.create_task(handler.on_interact_word(client, generate_type(models.InteractWordCommand, {
            'data': {'msg_type': 1}
        })))
        c = await asl.get_call(target=ui.add_record, f='async')
        assert "进入" in c.args[0].segments[2].text
        c.set_result(None)
        await t


@pytest.mark.asyncio
async def test_gift_threshold():
    with AsyncStoryline() as asl:
        ui = asl.add_async_mock(mock_class=MockUI)
        client = asl.add_async_mock()

        handler = DanmakuPHandler(ui=ui, gift_threshold=10)

        await handler.on_send_gift(client, generate_type(models.GiftCommand, {
            'data': {'price': 1000, 'num': 1000, 'coin_type': 'silver'}
        }))

        await handler.on_send_gift(client, generate_type(models.GiftCommand, {
            'data': {'price': 0, 'coin_type': 'gold'}
        }))


def test_danmakup_assert_ignore_less_than_dim():
    with pytest.raises(ValidationError):
        DanmakuPHandler(ignore_rate=1.0)


def test_danmakup_split_flags():
    handler = DanmakuPHandler(test_flags="a,b,c")
    assert handler.test_flags == ['a', 'b', 'c']
