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


class Richy(BaseStreamView):
    uic: Literal['richy'] = 'richy'
    verbose: int = 0
    datetime_format: str = '[%Y-%m-%d %H:%M:%S]'

    palette: list[str] = 'red,green,yellow,blue,magenta,cyan'.split(',')
    currency_palette: ThresholdPalette = ThresholdPalette.model_validate([
        (1000, 'on red'), (500, 'on orange3'), (100, 'on yellow'), (50, 'on cyan'), (30, 'on blue')])
    importance_palette: ThresholdPalette = ThresholdPalette.model_validate([
        (40, 'on red'), (30, 'on orange3'), (20, 'on cyan'), (10, 'white'), (0, 'dim')])

    def get_currency_style(self, currency) -> str:
        return self.currency_palette.get(currency)

    def get_importance_style(self, importance) -> str:
        return self.importance_palette.get(importance)

    def get_color_see_see(self, text):
        return self.palette[hash(text) % len(self.palette)]

    def format_record(self, record: Record) -> RichRenderable:
        s = rf"[cyan dim]{escape(record.time.astimezone().strftime(self.datetime_format))}[/] "
        d = {}
        m = count(1)
        for seg in record.segments:
            match seg:
                case PlainText(text=text) | Picture(alt=text):
                    s += escape(text)
                case Anchor(text=text, href=href):
                    s += f"[blue u link={href}]{text}[/]"
                case User(name=name, uid=uid):
                    s += f"[rgb(251,114,153) u link=https://space.bilibili.com/{uid}]{name}[/]"
                case Room(owner_name=name, room_id=room_id):
                    s += f"[rgb(255,212,50) u link=https://live.bilibili.com/{room_id}]{name}的直播间[/]"
                case RoomTitle(title=title, room_id=room_id):
                    s += f"[u link=https://live.bilibili.com/{room_id}]《[rgb(255,212,50)]{title}[/]》[/]"
                case ColorSeeSee(text=text):
                    s += f"[{self.palette[hash(text) % len(self.palette)]}]{escape(text)}[/]"
                case DebugInfo(text=text, info=info):
                    if self.verbose > 0:
                        k = f"{text}_{next(m)}"
                        s += f"\\[{k}...]"
                        d[k] = info
                    else:
                        s += f"(info...)"
                case Currency(price=price, mark=mark):
                    if price > 0:
                        style = self.get_currency_style(price)
                        if style:
                            s += f" [{style}]\\[{mark}{price}][/]"
                        else:
                            s += f" \\[{mark}{price}]"
                case Emoji(codepoint=cp):
                    s += f"{cp}\N{VS16}"
        res = [Text.from_markup(f"[{self.get_importance_style(record.importance)}]{s}")]
        for k, v in d.items():
            res.append(Panel.fit(JSON.from_data(v), title=f'[{k}]'))
        group = Group(*res, fit=True)
        return group  # noqa: RichRenderable is dynamic

    @cached_property
    def _console(self):
        return Console()

    async def add_record(self, record: Record, sticky=False):
        self._console.print(self.format_record(record))

    async def edit_record(self, key, *, record=None, sticky=None):
        if record is not None:
            self._console.print(self.format_record(record))

    async def remove(self, key):
        pass


if __name__ == '__main__':
    demo(Richy(verbose=1))
