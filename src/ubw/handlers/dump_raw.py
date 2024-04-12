import asyncio
import logging
from datetime import datetime, timezone, timedelta
from functools import cached_property

from aiotinydb import AIOTinyDB

from ._base import *
from ..clients import BilibiliUnauthorizedClient

logger = logging.getLogger('blive_dumpraw')


class DumpRawHandler(BaseHandler):
    cls: Literal['dump_raw'] = 'dump_raw'
    max_shard_length: timedelta = timedelta(days=1)
    room_id: int
    _living: bool = False
    _wait_sharding: asyncio.Future | None = None
    _sharder_task: asyncio.Task | None = None

    def start(self, client):
        self._sharder_task = asyncio.create_task(self.t_sharder())

    @cached_property
    def shard_start(self):
        return datetime.now(timezone(timedelta(seconds=8 * 3600)))

    @cached_property
    def db(self):
        fname = f"output/blive_dumpraw/{self.room_id}/{self.shard_start.strftime('%Y年%m月%d日%H点%M%S')}.json"
        logger.debug(f"[{self.room_id}] creating db: {fname}")
        db = AIOTinyDB(fname)
        return db

    async def process_one(self, client, command):
        cmd = command.get('cmd', '')
        if cmd in self.ignored_cmd:
            logger.debug(f"got a {cmd}, processed with ignore")
            return
        async with self.db as db:
            logger.debug(f"got a {cmd}, logged")
            db.insert(command)

    async def t_sharder(self):
        self._wait_sharding = asyncio.Future()
        while True:
            await self.m_new_shard()
            try:
                logger.debug(f"next sharding in {self.max_shard_length}")
                async with asyncio.timeout(self.max_shard_length.total_seconds()):
                    await self._wait_sharding
                    self._wait_sharding = asyncio.Future()
            except asyncio.TimeoutError:
                pass

    async def m_new_shard(self):
        async with BilibiliUnauthorizedClient() as client:
            info = await client.get_info_by_room(self.room_id)
        self._living = info.room_info.live_start_time is not None
        self.__dict__.pop('shard_start', None)
        self.__dict__.pop('db', None)
        async with self.db as db:
            db.insert(info.model_dump(exclude_defaults=True, by_alias=True))
