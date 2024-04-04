import asyncio
import base64
import json
import random
import string
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
import yarl

from ubw.clients import MockBilibiliClient, WSWebCookieLiveClient
from ubw.clients._b_base import USER_AGENT
from ubw.clients._livebase import HEADER_STRUCT, Operation, AuthError
from ubw.clients.testing import MockWebsocket
from ubw.handlers import MockHandler
from ubw.models import DanmuInfo


def generate_random_string(mark=None):
    tok = ''.join(random.choices(string.ascii_letters, k=16))
    if mark is None:
        return tok
    return f"<{mark}.{tok}>"


class Value:
    def __init__(self, value):
        self.value = value


class Checkpoint:
    def __init__(self):
        self._future = asyncio.Future()
        self._more_side_effect = None

    def back_conn(self, mock):
        def decorator(f):
            self._more_side_effect = f
            return f

        mock.side_effect = self.side_effect
        return decorator

    def reach(self, val=None):
        if not self._future.done():
            self._future.set_result(val)

    def side_effect(self, *args, **kwargs):
        self.reach()
        return self._more_side_effect(*args, **kwargs)

    def is_reached(self):
        return self._future.done()

    def __await__(self):
        yield from self._future.__await__()


@pytest.mark.asyncio
async def test_wsweb():
    room_id = 123
    heartbeat_interval = 0.7
    self_uid = 343

    if heartbeat_interval % 1 == 0:
        heartbeat_interval += 0.01

    buvid3 = generate_random_string('buvid3')
    token = generate_random_string('token')

    bilibili_client = MockBilibiliClient()
    client = WSWebCookieLiveClient(room_id=room_id,
                                   bilibili_client=bilibili_client,
                                   heartbeat_interval=heartbeat_interval)
    handler = MockHandler()

    session: Mock = bilibili_client.make_session.return_value
    session.close = AsyncMock()

    if TYPE_CHECKING:
        bilibili_client.__aenter__: AsyncMock
        session.cookie_jar.filter_cookies: Mock
        bilibili_client.get_danmaku_server: AsyncMock
        session.ws_connect: Mock
        session.close: AsyncMock

    checkpoint1 = Checkpoint()
    checkpoint2 = Checkpoint()
    checkpoint3 = Checkpoint()
    checkpoint4 = Checkpoint()
    checkpoint5 = Checkpoint()
    checkpoint_g = Checkpoint()
    checkpoint_heart = Checkpoint()

    @checkpoint1.back_conn(bilibili_client.__aenter__)
    def effect1():
        return bilibili_client

    session.cookie_jar.filter_cookies.return_value = {'DedeUserID': Value(str(self_uid)),
                                                      'buvid3': Value(buvid3)}

    @checkpoint2.back_conn(bilibili_client.get_danmaku_server)
    def effect2(r):
        return DanmuInfo.model_validate({
            'group': 'group',
            'business_id': 1,
            'refresh_row_factor': 1.0,
            'refresh_rate': 1,
            'max_delay': 1,
            'token': token,
            'host_list': [{
                'host': 'host_list.host',
                'port': 444,
                'wss_port': 445,
                'ws_port': 446,
            }],
        })

    websocket = MockWebsocket()

    @checkpoint3.back_conn(session.ws_connect)
    def effect3(*args, **kwargs):
        return websocket

    t = 0
    task = None

    async def ws():
        nonlocal t
        nonlocal task
        t += 1
        if t == 1:
            checkpoint4.reach()
            b64 = (b'AAAAVQAQAAMAAAAFAAAAAAsggAAAAEEAEAAAAAAABQAAAAB7ImNtZCI6Ik9OTElO'
                   b'RV9SQU5LX0NPVU5UIiwiZGF0YSI6eyJjb3VudCI6MTAyOH19Aw==')
            binary = base64.decodebytes(b64)
            return aiohttp.WSMessage(aiohttp.WSMsgType.BINARY, binary, None)
        elif t == 2:
            checkpoint5.reach()
            b64 = (b'AAAAfQAQAAMAAAAFAAAAABtpAFA8FO/SPlSd9SwZYlTORuGRf0XVAAVqe1skZg99'
                   b'Lf42RN8hp54hGnOTLCIwodMiX0Vks02kTicnBzkgP2tJ1pZQWACWU47aEolbi856'
                   b'uX5iQOZczmJwz97BTdzTPDGlFxYSQROw67m1jwI=')
            binary = base64.decodebytes(b64)
            return aiohttp.WSMessage(aiohttp.WSMsgType.BINARY, binary, None)
        else:
            checkpoint_g.reach()
            await asyncio.Future()  # wait forever, only to be stopped from outside

    websocket.side_effect = ws

    client.add_handler(handler)

    original_sleep = asyncio.sleep

    try:
        async with asyncio.timeout(20):
            with patch('asyncio.sleep') as patch_sleep:
                t_retry = 0
                t_heart = 0

                async def sleep(secs):
                    nonlocal t_heart
                    nonlocal t_retry
                    if secs == 0:  # call soon
                        await original_sleep(0)
                    elif secs % 1 > 0:  # heart beat interval
                        t_heart += 1
                        if t_heart == 1:  # first time
                            await checkpoint_g
                        elif t_heart == 2:
                            checkpoint_heart.reach()
                            await asyncio.Future()  # wait forever
                        # await original_sleep(0)
                    else:  # retry interval
                        # await checkpoint_g
                        await original_sleep(0)

                patch_sleep.side_effect = sleep

                client.start()

                def pre_check_send_bytes(await_args, operation) -> bytes:
                    assert await_args.kwargs == {}
                    assert len(await_args.args) == 1
                    b = await_args.args[0]
                    assert isinstance(b, bytes)
                    ht = HEADER_STRUCT.unpack_from(b, 0)
                    assert ht[0] == len(b)
                    assert ht[1] == HEADER_STRUCT.size
                    assert ht[2] == 1
                    assert ht[3] == operation
                    assert ht[4] == 1
                    return json.loads(b[HEADER_STRUCT.size:].decode())

                await checkpoint1
                bilibili_client.__aenter__.assert_awaited_once_with()

                await checkpoint2
                session.cookie_jar.filter_cookies.assert_called_once_with(yarl.URL('https://www.bilibili.com/'))
                bilibili_client.get_danmaku_server.assert_awaited_once_with(room_id)

                await checkpoint3
                session.ws_connect.assert_called_once_with(f"wss://host_list.host:445/sub",
                                                           headers={'User-Agent': USER_AGENT},
                                                           receive_timeout=heartbeat_interval + 5)

                await checkpoint4

                assert websocket.send_bytes.await_count == 1
                data = pre_check_send_bytes(websocket.send_bytes.await_args, Operation.AUTH)
                assert data == {
                    'uid': self_uid,
                    'roomid': room_id,
                    'protover': 3,
                    'platform': 'web',
                    'type': 2,
                    'key': token,
                    'buvid': buvid3,
                }

                await checkpoint5

                handler.handle.assert_awaited_once_with(client, {
                    'cmd': 'ONLINE_RANK_COUNT',
                    'data': {'count': 1028}})

                await checkpoint_g
                handler.handle.assert_awaited_with(client, {
                    'cmd': 'WATCHED_CHANGE',
                    'data': {'num': 130, 'text_small': "130", 'text_large': "130人看过"}})

                await checkpoint_heart
                assert websocket.send_bytes.await_count == 2
                data = pre_check_send_bytes(websocket.send_bytes.await_args, Operation.HEARTBEAT)
                assert data == {}

                async def stopper():
                    await original_sleep(0)  # several call soon to make sure join is joining
                    await original_sleep(0)
                    await original_sleep(0)
                    await original_sleep(0)
                    await original_sleep(0)
                    client.stop()

                stopper_task = asyncio.create_task(stopper())
                with pytest.raises(asyncio.CancelledError):
                    await client.join()
                await client.close()

                session.close.assert_awaited_once_with()
    except asyncio.TimeoutError as e:
        expected = []
        actual = []
        for k, v in locals().items():
            if isinstance(v, Checkpoint):
                expected.append(k)
                if v.is_reached():
                    actual.append(k)
        raise AssertionError(f"""expected checkpoint not reached.\n"""
                             f"""Expected: {" ".join(expected)}\n"""
                             f"""Actual:   {" ".join(actual)}\n""") from None


@pytest.mark.asyncio
async def test_auth_error_reconnect():
    room_id = 123
    heartbeat_interval = 0.7
    self_uid = 343

    buvid3 = generate_random_string('buvid3')
    token = generate_random_string('token')

    bilibili_client = MockBilibiliClient()
    client = WSWebCookieLiveClient(room_id=room_id,
                                   bilibili_client=bilibili_client,
                                   heartbeat_interval=heartbeat_interval)

    session: Mock = bilibili_client.make_session.return_value
    session.close = AsyncMock()

    checkpoint1 = Checkpoint()
    checkpoint2 = Checkpoint()
    checkpoint3 = Checkpoint()
    checkpoint4 = Checkpoint()
    checkpoint5 = Checkpoint()
    checkpoint6 = Checkpoint()

    @checkpoint1.back_conn(bilibili_client.__aenter__)
    def effect1():
        return bilibili_client

    session.cookie_jar.filter_cookies.return_value = {'DedeUserID': Value(str(self_uid)),
                                                      'buvid3': Value(buvid3)}

    @checkpoint2.back_conn(bilibili_client.get_danmaku_server)
    def effect2(r):
        return DanmuInfo.model_validate({
            'group': 'group',
            'business_id': 1,
            'refresh_row_factor': 1.0,
            'refresh_rate': 1,
            'max_delay': 1,
            'token': token,
            'host_list': [{
                'host': 'host_list.host',
                'port': 444,
                'wss_port': 445,
                'ws_port': 446,
            }],
        })

    websocket = MockWebsocket()

    @checkpoint3.back_conn(session.ws_connect)
    def effect3(*args, **kwargs):
        return websocket

    t = 0

    async def ws():
        nonlocal t
        t += 1
        if t == 1:
            checkpoint4.reach()
            raise AuthError
        elif t == 2:
            checkpoint5.reach()
            raise ConnectionError
        else:
            checkpoint6.reach()
            await asyncio.Future()

    websocket.side_effect = ws

    try:
        async with asyncio.timeout(5):
            with patch('asyncio.sleep') as patch_sleep:
                async def sleep(secs):
                    if secs % 1 > 0:
                        await asyncio.Future()
                    else:
                        return

                patch_sleep.side_effect = sleep

                client.start()

                await checkpoint1
                await checkpoint2
                await checkpoint3
                await checkpoint4
                await checkpoint5
                await checkpoint6

                assert client.user_ident == f'u={self_uid}|r={room_id}'
                assert bilibili_client.get_danmaku_server.await_count == 2

                with pytest.raises(asyncio.CancelledError):
                    await client.stop_and_close()

    except asyncio.TimeoutError as e:
        expected = []
        actual = []
        for k, v in locals().items():
            if isinstance(v, Checkpoint):
                expected.append(k)
                if v.is_reached():
                    actual.append(k)
        raise AssertionError(f"""expected checkpoint not reached.\n"""
                             f"""Expected: {" ".join(expected)}\n"""
                             f"""Actual:   {" ".join(actual)}\n""") from None
