import asyncio
import logging
import sys
import weakref

try:
    from tinyflux import TinyFlux, Point
except ImportError:
    sys.exit("tinyflux is not installed, try install this with extra `tinyflux`")

import blivedm

logger = logging.getLogger('bliflux')


class BliveTinyFluxHandler(blivedm.BaseHandler):
    def __init__(self, btf: 'BliveTinyFlux', **p):
        self.btfwf = weakref.ref(btf)
        super().__init__(**p)

    async def on_danmu_msg(self, client, message):
        btf = self.btfwf()
        if btf is None:
            return
        btf.add_point(Point(
            measurement=f"{btf.room_id}_DANMAKU",
            time=message.info.timestamp,
            tags={
                "uname": message.info.uname,
                "uid": str(message.info.uid),
                "medal": f"{message.info.medal_name}|{message.info.medal_level}",
                "medal_room_id": str(message.info.medal_room_id),
            },
        ))

    async def on_send_gift(self, client, message):
        btf = self.btfwf()
        if btf is None:
            return
        btf.add_point(Point(
            measurement=f"{btf.room_id}_GIFT",
            time=message.data.timestamp,
            tags={
                "uname": message.data.uname,
                "uid": str(message.data.uid),
                "gift_name": message.data.giftName,
            },
            fields={
                f"price_{message.data.coin_type}": f"{message.data.price}"
            }
        ))

    async def on_guard_buy(self, client, message):
        btf = self.btfwf()
        if btf is None:
            return
        btf.add_point(Point(
            measurement=f"{btf.room_id}_GUARD",
            time=message.data.start_time,
            tags={
                "uname": message.data.username,
                "uid": str(message.data.uid),
                "gift_name": message.data.gift_name,
            },
            fields={
                "gold": f"{message.data.price}",
            },
        ))

    async def on_super_chat_message(self, client, message):
        btf = self.btfwf()
        if btf is None:
            return
        btf.add_point(Point(
            measurement=f"{btf.room_id}_SC",
            time=message.data.start_time,
            tags={
                "uname": message.data.user_info.uname,
                "uid": str(message.data.uid),
                "message": message.data.message,
            },
            fields={
                "gold": f"{message.data.price}",
            },
        ))


class BliveTinyFlux:
    def __init__(self, db, room_id):
        self.db = TinyFlux(db)
        self.room_id = room_id
        self.client = blivedm.BLiveClient(room_id)
        self.handler = BliveTinyFluxHandler(btf=self)
        self.client.add_handler(self.handler)
        self.task = None

    def start(self):
        self.task = asyncio.create_task(self.run())

    async def join(self):
        if self.task is None:
            return
        await asyncio.shield(self.task)

    async def run(self):
        self.client.start()
        await self.client.join()

    def add_point(self, p: Point):
        self.db.insert(p)
