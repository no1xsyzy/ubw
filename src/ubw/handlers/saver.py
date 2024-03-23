import asyncio
import logging
from datetime import datetime, timezone, timedelta
from functools import cached_property

from aiotinydb import AIOTinyDB, AIOJSONStorage
from aiotinydb.middleware import AIOMiddleware
from tinydb_serialization import SerializationMiddleware as _SyncSerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer, Serializer

from ._base import *
from ..clients import BilibiliUnauthorizedClient

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
    _wait_sharding: asyncio.Future | None = None
    _sharder_task: asyncio.Task | None = None

    def start(self, client):
        self._sharder_task = asyncio.create_task(self.t_sharder())
        super().start(client)

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
        logger.info(f"{message.info.uname} ({message.info.uid}): {message.info.msg}")
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_send_gift(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_guard_buy(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_super_chat_message(self, client, message):
        logger.info(f"{message.data.user_info.uname} ({message.data.uid}): "
                    f"{message.data.message} (¥{message.data.price})")
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_room_change(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_live(self, client, message):
        if not self._living:
            await self.m_shard_now()

    async def on_preparing(self, client, message):
        if self._living:
            await self.m_shard_now()

    async def on_room_block_msg(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_warning(self, client, message):
        async with self.db as db:
            db.insert(message.model_dump(exclude_defaults=True, by_alias=True))

    async def on_unknown_cmd(self, client, command, err):
        async with self.db as db:
            db.insert({**command, 'UNKNOWN': True})
        await super().on_unknown_cmd(client, command, err)

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

    async def m_shard_now(self):
        self._wait_sharding.set_result(None)

    async def m_new_shard(self):
        async with BilibiliUnauthorizedClient() as client:
            info = await client.get_info_by_room(self.room_id)
        self._living = info.room_info.live_start_time is not None
        self.__dict__.pop('shard_start', None)
        self.__dict__.pop('db', None)
        async with self.db as db:
            db.insert(info.model_dump(exclude_defaults=True, by_alias=True))
