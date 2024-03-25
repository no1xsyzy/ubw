import asyncio
import sys
import warnings
from functools import wraps
from typing import Callable

from .clients import BilibiliCookieClient, WSWebCookieLiveClient, HandlerInterface, BilibiliClientABC
from .handlers import BaseHandler

__all__ = ('listen_to_all', 'sync')


async def listen_to_all(
        room_ids: list[int],
        handler: BaseHandler = None,
        handler_factory: Callable[[int], HandlerInterface] = None,
        b_client: BilibiliClientABC = None,
):
    if handler is None and handler_factory is None:
        raise ValueError("neither handler nor handler_factory is specified, useless")

    async def g(b):
        clients: dict[int, WSWebCookieLiveClient] = {}
        for room_id in room_ids:
            if room_id in clients:
                client = clients[room_id]
            else:
                clients[room_id] = client = \
                    WSWebCookieLiveClient(bilibili_client=b, bilibili_client_owner=False, room_id=room_id)
            client.add_handler(handler if handler is not None else handler_factory(room_id))
            handler.start(client)
            await handler.astart(client)
            client.start()

        try:
            await asyncio.gather(*(client.join() for client in clients.values()))
        finally:
            await asyncio.gather(*(client.stop_and_close() for client in clients.values()))

    if b_client is None:
        warnings.warn('b_client should be passed')
        async with BilibiliCookieClient(cookie_file='cookies.txt') as b_client:
            await g(b_client)
    else:
        await g(b_client)


def sync(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return asyncio.run(f(*args, **kwargs))
        except KeyboardInterrupt:
            print("...user abort...", file=sys.stderr)

    return wrapper
