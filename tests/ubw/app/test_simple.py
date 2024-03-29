import asyncio

import pytest

from ubw.app import SimpleApp
from ubw.clients import MockClient
from ubw.handlers import MockHandler


@pytest.mark.asyncio
async def test_simple():
    client = MockClient(room_id=42)
    handler = MockHandler()
    app = SimpleApp(client=client, handler=handler)

    app.start()
    await app.join()
    await app.close()

    client.add_handler.assert_called_once_with(handler)
    handler.start.assert_called_once_with(client)
    handler.astart.assert_awaited_once_with(client)
    client.start.assert_called_once_with()
    client.join.assert_awaited_once_with()
    client.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_simple_break():
    client = MockClient(room_id=42)
    handler = MockHandler()
    app = SimpleApp(client=client, handler=handler)

    started = asyncio.Future()

    async def sleep_hour():
        started.set_result(None)
        await asyncio.sleep(3600)

    async def p():
        app.start()
        await app.join()
        # do not `try: ... finally: await app.close()` because this is going to `await app.stop_and_close()`

    client.join.side_effect = sleep_hour
    task = asyncio.create_task(p())
    await started

    client.add_handler.assert_called_once_with(handler)
    handler.start.assert_called_once_with(client)
    handler.astart.assert_awaited_once_with(client)
    client.start.assert_called_once_with()
    client.join.assert_awaited_once_with()
    with pytest.raises(asyncio.CancelledError):
        await app.stop_and_close()
    client.close.assert_awaited_once_with()
