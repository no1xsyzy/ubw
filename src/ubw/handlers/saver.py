import asyncio
import logging
import sys
from datetime import datetime, timezone, timedelta
from functools import cached_property

try:
    from tinydb import TinyDB, Query
    from tinydb.storages import JSONStorage
    from tinydb_serialization import SerializationMiddleware as _SyncSerializationMiddleware
    from tinydb_serialization.serializers import DateTimeSerializer, Serializer
    from aiotinydb import AIOTinyDB, AIOJSONStorage
    from aiotinydb.middleware import AIOMiddleware
except ImportError as e:
    sys.exit(f"{e.name} is not installed, try install this with extra `tinydb`")

from ..clients import BilibiliUnauthorizedClient
from ._base import *

logger = logging.getLogger('blive_saver')


class SerializationMiddleware(_SyncSerializationMiddleware, AIOMiddleware):
    pass


class TimeDeltaSerializer(Serializer):
    OBJ_CLASS = timedelta

    def encode(self, obj):
        return str(obj.total_seconds())

    def decode(self, s):
        return timedelta(seconds=float(s))


class SaverHandler(BaseHandler):
    cls: Literal['saver'] = 'saver'
    max_shard_length: timedelta = timedelta(days=1)
    room_id: int
    _living: bool = False
    _wait_sharding: asyncio.Task | None = None

    async def start(self):
        await self.m_new_shard()

    @cached_property
    def shard_start(self):
        return datetime.now(timezone(timedelta(seconds=8 * 3600)))

    @cached_property
    def db(self):
        fname = f"output/blive_saver/{self.room_id}/{self.shard_start.strftime('%Y年%m月%d日%H点%M%S')}.json"
        logger.debug(f"[{self.room_id}] creating db: {fname}")
        # you need serialization for each TinyDB instance, or it will always write to last instance
        serialization = SerializationMiddleware(AIOJSONStorage)
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        serialization.register_serializer(TimeDeltaSerializer(), 'timedelta')
        db = AIOTinyDB(fname, storage=serialization)
        return db

    async def on_danmu_msg(self, client, message):
        logger.info(f"[{self.room_id}] {message.info.uname} ({message.info.uid}): "
                    f"{message.info.msg}")
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_send_gift(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_guard_buy(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_super_chat_message(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_room_change(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_live(self, client, message):
        if not self._living:
            await self.m_new_shard()

    async def on_preparing(self, client, message):
        if self._living:
            await self.m_new_shard()

    async def on_room_block_msg(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def on_warning(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump())

    async def m_new_shard(self):
        self.__dict__.pop('shard_start', None)
        self.__dict__.pop('db', None)
        info = await BilibiliUnauthorizedClient().get_info_by_room(self.room_id)
        self._living = info.room_info.live_start_time is not None
        async with self.db as db:
            db.insert(info.model_dump())
        if self._wait_sharding is not None:
            self._wait_sharding.cancel("new shard")
        self._wait_sharding = asyncio.create_task(self.m_new_shard_waiting())

    async def m_new_shard_waiting(self):
        if 'shard_start' not in self.__dict__:
            return
        next_sharding = self.shard_start + self.max_shard_length
        logger.info(f"[{self.room_id}] scheduled sharding: {next_sharding}")
        delay = next_sharding - datetime.now(timezone(timedelta(seconds=8 * 3600)))
        await asyncio.sleep(delay.total_seconds())
        logger.info(f"[{self.room_id}] sharding")
        await asyncio.shield(self.m_new_shard())
