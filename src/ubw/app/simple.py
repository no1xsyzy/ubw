from ubw.clients import LiveClient
from ubw.handlers import Handler
from ._base import *


class SimpleApp(BaseApp):
    cls: Literal['simple'] = 'simple'
    client: LiveClient
    handler: Handler

    async def _run(self):
        self.client.add_handler(self.handler)
        self.handler.start(self.client)
        await self.handler.astart(self.client)
        self.client.start()
        await self.client.join()

    async def close(self):
        await self.client.close()
