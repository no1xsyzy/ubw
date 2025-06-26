import abc
import asyncio
from datetime import datetime
from operator import itemgetter
from typing import Literal

import unicodedata
from pydantic import BaseModel, Field, RootModel, model_validator

__all__ = (
    'Segment',
    'PlainText', 'Anchor', 'User', 'Room', 'RoomTitle', 'ColorSeeSee', 'DebugInfo', 'Currency', 'Picture', 'LineBreak',
    'Emoji',
    'Record',
    'BaseStreamView', 'Literal', 'Field', 'ThresholdPalette',
    'demo',
)


class Segment(BaseModel):
    type: str


class PlainText(Segment):
    type: Literal['t'] = 't'
    text: str


class Anchor(Segment):
    type: Literal['a'] = 'a'
    text: str
    href: str


class User(Segment):
    type: Literal['user'] = 'user'
    name: str
    uid: int
    face: str = ''


class Room(Segment):
    type: Literal['room'] = 'room'
    owner_name: str
    room_id: int


class RoomTitle(Segment):
    type: Literal['room_title'] = 'room_title'
    title: str
    room_id: int


class ColorSeeSee(Segment):
    type: Literal['color_see_see'] = 'color_see_see'
    text: str


class DebugInfo(Segment):
    type: Literal['debug'] = 'debug'
    text: str = 'DEBUG'
    info: dict


class Currency(Segment):
    type: Literal['currency'] = 'currency'
    price: float
    mark: str = '￥'


class Picture(Segment):
    type: Literal['picture'] = 'picture'
    url: str
    alt: str


class Emoji(Segment):
    type: Literal['emoji'] = 'emoji'
    name: str
    codepoint: str

    @model_validator(mode='before')
    @classmethod
    def validates(cls, data):
        if 'name' in data and 'codepoint' in data:
            assert unicodedata.lookup(data['name']) == data['codepoint'], 'name and codepoint does not match'
        elif 'name' in data:
            data['codepoint'] = unicodedata.lookup(data['name'])
        elif 'codepoint' in data:
            data['name'] = unicodedata.name(data['codepoint'])
        else:
            raise ValueError('any of name and codepoint should be specified')
        return data


class LineBreak(Segment):
    type: Literal['line_break'] = 'line_break'


class Record(BaseModel):
    """
    :var importance: determines visibility.
        generally trivial=0 normal=10 notice=20 essential=30 fatal=40
    """
    segments: list[Segment]
    time: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    importance: int = 10


class BaseStreamView(BaseModel, abc.ABC):
    uic: str

    @abc.abstractmethod
    async def add_record(self, record: Record, sticky: str | bool = False): ...

    @abc.abstractmethod
    async def edit_record(self, key, *, record: Record | None = None, sticky: str | bool | None = None): ...

    @abc.abstractmethod
    async def remove(self, key): ...

    async def start(self): ...

    async def stop(self): ...

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


async def ademo(ui: BaseStreamView, interval=0.5):  # pragma: no cover
    import logging
    import random
    import string
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
    )
    async with ui:
        keys = []
        while True:
            match random.randint(0, 10):
                case 0:
                    await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text="text"),
                        PlainText(text=" "),
                        Anchor(text="text", href="href"),
                        PlainText(text=" "),
                        User(name="elza", uid=1521415),
                        PlainText(text=" "),
                        Room(owner_name="elza", room_id=81004),
                        PlainText(text=" "),
                        RoomTitle(title="直播间标题", room_id=81004),
                        PlainText(text=" "),
                        DebugInfo(info={'LOVE': '❤️'})
                    ]))
                case 1:
                    name: str = ''.join(random.choice(string.digits) for _ in range(8))
                    key = await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"This is sticky - {name}"),
                    ]), sticky=True)
                    keys.append((name, key))
                case 2:
                    if not keys:
                        continue
                    k = random.choice(range(len(keys)))
                    name, key = keys.pop(k)
                    await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"sticky {name} is going to be removed (not all ui support this)")
                    ]))
                    await asyncio.sleep(interval)
                    await ui.remove(key)
                    await asyncio.sleep(interval)
                    await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"sticky {name} should be removed (not all ui support this)")
                    ]))
                case 3 | 4 | 5:
                    await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text="ColorSeeSee's use color to help distinguishing different but similar texts "),
                        ColorSeeSee(text=f"ColorSeeSee/{random.randint(0, 9)}"),
                    ]))
                case _:
                    await ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text="dummy text"),
                    ]))
            await asyncio.sleep(interval)


class ThresholdPalette(RootModel[list[tuple[int, str]]]):
    root: list[tuple[int, str]]

    @model_validator(mode='after')
    def sort(self):
        self.root.sort(key=itemgetter(0), reverse=True)
        return self

    def get(self, val: int) -> str:
        for i, s in self.root:
            if val >= i:
                return s
        return ''


def demo(ui: BaseStreamView, interval=0.5):  # pragma: no cover
    try:
        asyncio.run(ademo(ui, interval))
    except KeyboardInterrupt:
        pass
