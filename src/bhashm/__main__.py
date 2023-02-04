import asyncio

from . import listen_to_all

asyncio.get_event_loop().run_until_complete(listen_to_all())
