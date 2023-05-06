from dataclasses import dataclass
from datetime import datetime

import aiohttp
import lxml.html


@dataclass
class Danmaku:
    t: datetime
    msg: str
    space_id: int


@dataclass
class Entrance:
    t: datetime
    space_id: int
    area_name: str


@dataclass
class Gift:
    t: datetime
    space_id: int
    gift: str
    cost: float


async def gank(uid, road="ablive_dm", offset="0"):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        while True:
            async with session.get(f"https://biligank.com/live/{road}?uid={uid}&offset={offset}") as resp:
                xml = await resp.text()
                doc = lxml.html.fragments_fromstring(xml)
                for div_by_liver in doc[:-1]:
                    _, space_id, camel_date = div_by_liver.getchildren()[1].attrib['id'].split("-")
                    for dmk in div_by_liver.getchildren()[1].getchildren()[0].getchildren():
                        time, msg = dmk.text_content().strip().split(" -> ")
                        t = datetime.strptime(f"{camel_date} {time}", "%Y_%m_%d %H:%M:%S")
                        yield Danmaku(space_id=space_id, t=t, msg=msg)
                anchor = doc[-1].xpath("""//a[@id="pagination-more"]""")
                if not anchor:
                    break
                uid = anchor[0].attrib['data-uid']
                road = anchor[0].attrib['data-road']
                offset = anchor[0].attrib['data-offset']


class Ganker:
    _session: aiohttp.ClientSession | None

    def __init__(self, uid, road="ablive_dm", offset="0"):
        self.uid = uid
        self.road = road
        self.offset = offset
        self.items = []
        self.ended = False
        self._session = None
        self._created_session = False

    @property
    def session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            self._created_session = True
        return self._session

    @session.setter
    def session(self, sess):
        if self._created_session:
            self._session.close()
            self._created_session = False
        self._session = sess

    async def fetch_more(self):
        if self.ended:
            return
        async with self.session.get(
                f"https://biligank.com/live/{self.road}?uid={self.uid}&offset={self.offset}") as resp:
            xml = await resp.text()
            doc = lxml.html.fragments_fromstring(xml)
            for div_by_liver in doc[:-1]:
                _, space_id, camel_date = div_by_liver.getchildren()[1].attrib['id'].split("-")
                for dmk in div_by_liver.getchildren()[1].getchildren()[0].getchildren():
                    time, msg = dmk.text_content().strip().split(" -> ")
                    t = datetime.strptime(f"{camel_date} {time}", "%Y_%m_%d %H:%M:%S")
                    self.items.append(Danmaku(space_id=space_id, t=t, msg=msg))
            anchor = doc[-1].xpath("""//a[@id="pagination-more"]""")
            if not anchor:
                self.ended = True
            self.uid = anchor[0].attrib['data-uid']
            self.road = anchor[0].attrib['data-road']
            self.offset = anchor[0].attrib['data-offset']

    async def fetch_all(self):
        while not self.ended:
            await self.fetch_more()
