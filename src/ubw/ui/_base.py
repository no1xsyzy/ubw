import abc
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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


class Record(BaseModel):
    segments: list[Segment]
    time: datetime = Field(default_factory=datetime.now)


class BLiveUI(BaseModel, abc.ABC):
    uic: str

    @abc.abstractmethod
    def add_record(self, record: Record, sticky: bool = False): ...

    @abc.abstractmethod
    def edit_record(self, key, record: Record): ...

    @abc.abstractmethod
    def remove(self, key): ...

    @abc.abstractmethod
    def unstick(self, key): ...

    @abc.abstractmethod
    def unstick_before(self, key, before): ...

    def start(self):
        pass

    def stop(self):
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def demo(ui: BLiveUI, interval=0.5):
    import time
    import random
    import string
    with ui:
        keys = []
        while True:
            match random.randint(0, 10):
                case 0:
                    ui.add_record(Record(time=datetime.now(), segments=[
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
                    name = ''.join(random.choice(string.digits) for _ in range(8))
                    key = ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"This is sticky - {name}"),
                    ]), sticky=True)
                    keys.append((name, key))
                case 2:
                    if not keys:
                        continue
                    k = random.choice(range(len(keys)))
                    name, key = keys.pop(k)
                    ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"sticky {name} is going to be removed (not all ui support this)")
                    ]))
                    time.sleep(interval)
                    ui.remove(key)
                    time.sleep(interval)
                    ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text=f"sticky {name} should be removed (not all ui support this)")
                    ]))
                case 3 | 4 | 5:
                    ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text="ColorSeeSee's use color to help distinguishing different but similar texts "),
                        ColorSeeSee(text=f"ColorSeeSee/{random.randint(0, 9)}"),
                    ]))
                case _:
                    ui.add_record(Record(time=datetime.now(), segments=[
                        PlainText(text="dummy text"),
                    ]))
            time.sleep(interval)
