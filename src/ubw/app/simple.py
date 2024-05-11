import asyncio

from ubw.clients import LiveClient
from ubw.handlers import Handler
from ._base import *


class SimpleApp(BaseApp):
    cls: Literal['simple'] = 'simple'
    client: LiveClient
    handler: Handler

    async def _run(self):
        self.client.add_handler(self.handler)
        await self.handler.start(self.client)
        await self.client.start()

    async def join(self):
        await self._task
        await asyncio.gather(self.client.join(), self.handler.join())

    async def stop(self):
        await self.client.stop()
        await self.handler.stop()

    async def close(self):
        await self.client.close()
        await self.handler.close()
