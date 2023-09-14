from functools import cached_property
from itertools import count

from rich.abc import RichRenderable
from rich.console import Console, Group
from rich.json import JSON
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from ._base import *

StickyKey = str


class Richy(BLiveUI):
    uic: Literal['richy'] = 'richy'
    verbose: int = 0
    datetime_format: str = '[%Y-%m-%d %H:%M:%S]'

    palette: list[str] = 'red,green,yellow,blue,magenta,cyan'.split(',')

    def format_record(self, record: Record) -> RichRenderable:
        s = rf"[cyan dim]{escape(record.time.strftime(self.datetime_format))}[/] "
        d = {}
        for seg in record.segments:
            match seg:
                case PlainText(text=text):
                    s += escape(text)
                case Anchor(text=text, href=href):
                    s += f"[blue u link={href}]{text}[/]"
                case User(name=name, uid=uid):
                    s += f"[rgb(251, 114, 153) u link=https://space.bilibili.com/{uid}]{name}[/]"
                case Room(owner_name=name, room_id=room_id):
                    s += f"[rgb(255,212,50) u link=https://live.bilibili.com/{room_id}]{name}的直播间[/]"
                case RoomTitle(title=title, room_id=room_id):
                    s += f"[u link=https://live.bilibili.com/{room_id}]《[rgb(255,212,50)]{title}[/]》[/]"
                case ColorSeeSee(text=text):
                    s += f"[{self.palette[hash(text) % len(self.palette)]}]{escape(text)}[/]"
                case DebugInfo(text=text, info=info):
                    if self.verbose > 0:
                        for i in count(1):
                            if (k := f"{text}_{i}") not in d:
                                s += f"\\[{k}...]"
                                d[k] = info
                                break
                    else:
                        s += f"(info...)"
        res = [Text.from_markup(s)]
        for k, v in d.items():
            res.append(Panel.fit(JSON.from_data(v), title=f'[{k}]'))
        group = Group(*res, fit=True)
        return group  # noqa: RichRenderable is dynamic

    @cached_property
    def _console(self):
        return Console()

    def add_record(self, record: Record, sticky=False):
        self._console.print(self.format_record(record))

    def edit_record(self, key, record: Record):
        self._console.print(self.format_record(record))

    def remove(self, key):
        pass

    def unstick(self, key):
        pass

    def unstick_before(self, key, before):
        pass


if __name__ == '__main__':
    demo(Richy(verbose=1))
