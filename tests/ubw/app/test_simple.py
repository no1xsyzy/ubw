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
