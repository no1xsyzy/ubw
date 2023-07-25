import asyncio
import sys
from functools import wraps
from typing import Callable

from .client import BLiveClient
from .handlers import BaseHandler

__all__ = ('listen_to_all', 'sync',)


async def listen_to_all(room_ids: list[int],
                        handler: BaseHandler = None, handler_factory: Callable[[int], BaseHandler] = None):
    if handler is None and handler_factory is None:
        raise ValueError("neither handler nor handler_factory is specified, useless")
    clients = {}
    for room_id in room_ids:
        clients[room_id] = client = BLiveClient(room_id)
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
