import argparse
import asyncio
import logging
import sys
from datetime import datetime, timezone, timedelta
from functools import cached_property

import toml
from rich.logging import RichHandler

try:
    from tinydb import TinyDB, Query
    from tinydb.storages import JSONStorage
    from tinydb_serialization import SerializationMiddleware as _SyncSerializationMiddleware
    from tinydb_serialization.serializers import DateTimeSerializer, Serializer
    from aiotinydb import AIOTinyDB, AIOJSONStorage
    from aiotinydb.middleware import AIOMiddleware
except ImportError as e:
    sys.exit(f"{e.name} is not installed, try install this with extra `tinydb`")

import blivedm
from bilibili import get_info_by_room

logger = logging.getLogger('blive_saver')

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        tracebacks_suppress=['logging', 'rich', 'tinydb'],
        show_path=False,
    )],
)


class SerializationMiddleware(_SyncSerializationMiddleware, AIOMiddleware):
    pass


class TimeDeltaSerializer(Serializer):
    OBJ_CLASS = timedelta

    def encode(self, obj):
        return str(obj.total_seconds())

    def decode(self, s):
        return timedelta(seconds=float(s))


class BliveTinyFluxHandler(blivedm.BaseHandler):
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
            db.insert(message.dict())

    async def on_send_gift(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def on_guard_buy(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def on_super_chat_message(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def on_room_change(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def on_live(self, client, message):
        if not self._living:
            await self.m_new_shard()

    async def on_preparing(self, client, message):
        if self._living:
            await self.m_new_shard()

    async def on_room_block_msg(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def on_warning(self, client, message):
        async with self.db as db:
            db.insert(message.dict())

    async def m_new_shard(self):
        self.__dict__.pop('shard_start', None)
        self.__dict__.pop('db', None)
        info = await get_info_by_room(self.room_id)
        self._living = info.room_info.live_start_time is not None
        async with self.db as db:
            db.insert(info.dict())
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


def main():
    room_ids = []

    parser = argparse.ArgumentParser('saver')

    parser.add_argument("-c", "--config", action='append')
    parser.add_argument("-r", "--room", action='append')

    args = parser.parse_args()

    for cf in args.config:
        with open(cf, 'r') as f:
            cfg = toml.load(f)
            room_ids = cfg['room_ids']
    for r in args.room:
        for room_id in (int(sri) for sri in r.split(",")):
            if room_id < 0:
                room_ids.remove(-room_id)
            elif room_id not in room_ids:
                room_ids.append(room_id)
    if not room_ids:
        sys.exit("no room_ids, this may be due to a config mistake")

    try:
        asyncio.run(blivedm.listen_to_all(room_ids, handler_factory=lambda r: BliveTinyFluxHandler(room_id=r)))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stderr)


if __name__ == '__main__':
    main()
