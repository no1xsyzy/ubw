import asyncio
import sys
from functools import wraps
from typing import Callable

from pydantic import BaseModel

from .clients import LiveClient, BilibiliCookieClient, WSWebCookieLiveClient, HandlerInterface
from .handlers import Handler, BaseHandler

__all__ = ('listen_to_all', 'sync', 'Application')


async def listen_to_all(room_ids: list[int],
                        handler: BaseHandler = None,
                        handler_factory: Callable[[int], HandlerInterface] = None):
    if handler is None and handler_factory is None:
        raise ValueError("neither handler nor handler_factory is specified, useless")
    clients: dict[int, WSWebCookieLiveClient] = {}
    async with BilibiliCookieClient(cookie_file='cookies.txt') as bclient:
        await bclient.read_cookie()
        for room_id in room_ids:
            if room_id in clients:
                client = clients[room_id]
            else:
                clients[room_id] = client = \
                    WSWebCookieLiveClient(bilibili_client=bclient, bilibili_client_owner=False, room_id=room_id)
            client.add_handler(handler if handler is not None else handler_factory(room_id))
            client.start()

        try:
            await asyncio.gather(*(client.join() for client in clients.values()))
        finally:
            await asyncio.gather(*(client.stop_and_close() for client in clients.values()))


def sync(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(f(*args, **kwargs))
        except KeyboardInterrupt:
            print("...user abort...", file=sys.stderr)

    return wrapper


class Application(BaseModel):
    client: LiveClient
    handler: Handler

    async def run(self):
        pass
