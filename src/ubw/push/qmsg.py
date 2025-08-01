import logging
from functools import cached_property

import aiohttp
from pydantic import BaseModel

logger = logging.getLogger('qmsg')

HOST = 'qmsg.zendee.cn'


class QMsgPusher(BaseModel):
    key: str

    # low config
    custom_host: str | None = None

    @cached_property
    def session(self):
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        logger.debug(f'created aiohttp session by QMsgPusher {session!r}')
        return session

    async def push(self, content: str):
        try:
            async with self.session.post(f"https://{self.custom_host or HOST}/jsend/{self.key}",
                                         json={'msg': content}) as resp:
                j = await resp.json()
            if j['success']:
                logger.debug("QMsg success")
            else:
                logger.warning("QMsg fail %s", j['reason'])
        except Exception as e:
            logger.exception('QMsg error', exc_info=e)

    async def close(self):
        await self.session.close()
