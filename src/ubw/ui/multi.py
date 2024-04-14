import asyncio

from ._base import *


class Multi(StreamUI):
    uic: Literal['multi'] = 'multi'

    uis: list[StreamUI] = []

    async def start(self):
        await asyncio.gather(*((ui.start() for ui in self.uis)))

    async def stop(self):
        await asyncio.gather(*((ui.stop() for ui in self.uis)))

    async def add_record(self, record: Record, sticky: str | bool = False):
        await asyncio.gather(*(ui.add_record(record, sticky) for ui in self.uis))

    async def edit_record(self, key, **kwargs):
        await asyncio.gather(*(ui.edit_record(key, **kwargs) for ui in self.uis))

    async def remove(self, key):
        await asyncio.gather(*(ui.remove(key) for ui in self.uis))
