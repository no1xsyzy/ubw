import asyncio
import logging
import sys
from datetime import datetime, timezone, timedelta
from functools import cached_property

try:
    from aiotinydb import AIOTinyDB
except ImportError as e:
    sys.exit(f"{e.name} is not installed, try install this with extra `tinydb`")

import blivedm
from bilibili import get_info_by_room

logger = logging.getLogger('blive_dumpraw')


class BliveDumpHandler(blivedm.BaseHandler):
    def __init__(self, *, room_id, max_shard_length=timedelta(days=1), **p):
        self.room_id = room_id
        self.max_shard_length = max_shard_length
        super().__init__(**p)
        self._living = False
        asyncio.create_task(self.m_new_shard())
        self._wait_sharding: asyncio.Task | None = None

    @cached_property
    def shard_start(self):
        return datetime.now(timezone(timedelta(seconds=8 * 3600)))

    @cached_property
    def db(self):
        fname = f"output/blive_dumpraw/{self.room_id}/{self.shard_start.strftime('%Y年%m月%d日%H点%M%S')}.json"
        logger.debug(f"[{self.room_id}] creating db: {fname}")
        db = AIOTinyDB(fname)
        return db

    async def handle(self, client, command):
        async with self.db as db:
            db.insert(command)

    async def m_new_shard(self):
        self.__dict__.pop('shard_start', None)
        self.__dict__.pop('db', None)
        info: dict = await get_info_by_room(self.room_id, type_=dict)
        self._living = info['room_info']['live_start_time'] is not None
        async with self.db as db:
            db.insert(info)
        if self._wait_sharding is not None:
            self._wait_sharding.cancel("new shard")
        self._wait_sharding = asyncio.create_task(self.m_new_shard_waiting())

    async def m_new_shard_waiting(self):
        if 'shard_start' not in self.__dict__:
            return
        next_sharding = self.shard_start + self.max_shard_length
        logger.info(f"[{self.room_id}] scheduled sharding: {next_sharding}")
        delay = next_sharding - datetime.now(timezone(timedelta(seconds=8 * 3600)))
        try:
            await asyncio.sleep(delay.total_seconds())
        except asyncio.CancelledError:
            raise
        else:
            logger.info(f"[{self.room_id}] sharding")
            asyncio.create_task(self.m_new_shard())
