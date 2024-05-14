import asyncio

from ubw.clients import LiveClient
from ubw.handlers import Handler
from ._base import *


class FullConnectApp(BaseApp):
    cls: Literal['fc'] = 'fc'
    clients: list[LiveClient]
    handlers: list[Handler]

    async def _run(self):
        for c in self.clients:
            for h in self.handlers:
                c.add_handler(h)
                await h.start(c)
            await c.start()

    async def join(self):
        await self._task
        await asyncio.gather(*(c.join() for c in self.clients), *(h.join() for h in self.handlers))

    async def stop(self):
        for c in self.clients:
            await c.stop()
        for h in self.handlers:
            await h.stop()

    async def close(self):
        for c in self.clients:
            await c.close()
        for h in self.handlers:
            await h.close()
