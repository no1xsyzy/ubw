import logging
import threading
from collections import OrderedDict
from functools import cached_property
from itertools import count
from typing import TypedDict

from rich.abc import RichRenderable
from rich.console import Group, Console, ConsoleOptions, RenderResult
from rich.json import JSON
from rich.live import Live
from rich.markup import escape
from rich.panel import Panel
from rich.segment import Segment as RichSegment
from rich.text import Text

from ._base import *

Key = str

logger = logging.getLogger('live')


class Info(TypedDict):
    is_sticky: bool
    unstick_before: set[Key]
    renderable: RichRenderable


class LiveStreamView(BaseStreamView):
    uic: Literal['live'] = 'live'
    verbose: int = 0
    alternate_screen: bool = False
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

    @cached_property
    def _records(self):
        return OrderedDict[Key, Info]()

    @cached_property
    def _live(self):
        return Live(self, screen=self.alternate_screen)

    @cached_property
    def _lock(self):
        return threading.RLock()

    async def start(self):
        self._live.start(True)

    async def stop(self):
        self._live.stop()

    def format_record(self, record: Record) -> 'RichRenderable':
        s = rf"[dim cyan]{escape(record.time.astimezone().strftime(self.datetime_format))}[/] "
        d = {}
        for seg in record.segments:
            match seg:
                case PlainText(text=text) | Picture(alt=text):
                    s += escape(text)
                case Anchor(text=text, href=href):
                    s += f"[blue u link={href}]{escape(text)}[/]"
                case User(name=name, uid=uid):
                    s += f"[{self.get_color_see_see(str(uid))} u link=https://space.bilibili.com/{uid}]{escape(name)}[/]"
                case Room(owner_name=name, room_id=room_id):
                    s += f"[rgb(255,212,50) u link=https://live.bilibili.com/{room_id}]{escape(name)}的直播间[/]"
                case RoomTitle(title=title, room_id=room_id):
                    s += f"[u link=https://live.bilibili.com/{room_id}]《[rgb(255,212,50)]{escape(title)}[/]》[/]"
                case ColorSeeSee(text=text):
                    s += f"[{self.get_color_see_see(text)}]{escape(text)}[/]"
                case DebugInfo(text=text, info=info):
                    if self.verbose > 0:
                        for i in count(1):
                            if (k := f"{text}_{i}") not in d:
                                s += f"\\[{k}...]"
                                d[k] = info
                                break
                    else:
                        s += f"(info...)"
                case Currency(price=price, mark=mark):
                    if price > 0:
                        style = self.get_currency_style(price)
                        if style:
                            s += f" [{style}]\\[{mark}{price}][/]"
                        else:
                            s += f" \\[{mark}{price}]"
        res = [Text.from_markup(f"[{self.get_importance_style(record.importance)}]{s}")]
        for k, v in d.items():
            res.append(Panel.fit(JSON.from_data(v), title=f'[{k}]'))
        group = Group(*res, fit=True)
        return group  # noqa: RichRenderable is dynamic

    def color_of(self, text):
        return self.palette[hash(text) % len(self.palette)]

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        with self._lock:
            height = options.height or console.height
            rendered: dict[Key, list[list[RichSegment]]] = {k: console.render_lines(v['renderable'], options)
                                                            for k, v in self._records.items()}
            nlines = sum(map(len, rendered.values()))
            extra_lines = nlines - height

            logger.debug('rendering %d lines in height %d', nlines, height)

            if extra_lines > 0:
                logger.debug('removing %d lines', extra_lines)

                import json
                logger.debug('renderables %s', json.dumps(
                    {k: str(v['renderable'].renderables) for k, v in self._records.items()}, indent=2))
                logger.debug('rendered %s', rendered)

                # process unstick_before
                former_k = None
                for k in reversed(self._records):
                    v = self._records[k]
                    if former_k in v['unstick_before'] or any(u not in self._records for u in v['unstick_before']):
                        v['is_sticky'] = False
                    former_k = k

                def remove_rendered(k):
                    nonlocal extra_lines
                    if extra_lines >= len(rendered[k]):
                        logger.debug('removing line[%s]: %s', k, rendered[k])
                        extra_lines -= len(rendered[k])
                        del rendered[k]
                        to_be_removed_keys.append(k)
                    else:
                        logger.debug('partially removing line[%s]: %s', k, rendered[k][:extra_lines])
                        rendered[k] = rendered[k][extra_lines:]
                        extra_lines = 0

                to_be_removed_keys = []
                for k, v in self._records.items():
                    if not v['is_sticky']:
                        remove_rendered(k)
                        if extra_lines == 0:
                            break
                else:  # too much sticky
                    for k, v in self._records.items():
                        if v['is_sticky']:
                            remove_rendered(k)
                            if extra_lines == 0:
                                break

                for k in to_be_removed_keys:
                    del self._records[k]

            result = []
            new_line = RichSegment.line()
            for k, v in self._records.items():
                if k in rendered:
                    rk = [j for rk in rendered[k] for j in rk]
                    if rk[-1].text.isspace():
                        rk.pop(-1)
                    # yield from itertools.chain.from_iterable(rk)
                    # yield new_line
                    result.extend(rk)
                    result.append(new_line)
            # logger.debug(f"{result!r}")
            yield Group(*result)

    def _generate_key(self):
        import string
        import random
        while True:
            key = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            if key not in self._records:
                return key

    async def add_record(self, record: Record, sticky=False):
        logger.debug(f'add_record()')
        with self._lock:
            key = self._generate_key()
            self._records[key] = Info(is_sticky=sticky, renderable=self.format_record(record), unstick_before=set())
            return key

    async def edit_record(self, key, *, record=None, sticky=None):
        logger.debug(f'edit_record()')
        with self._lock:
            if key in self._records:
                if record is not None:
                    self._records[key]['renderable'] = self.format_record(record)
                if sticky is not None:
                    self._records[key]['is_sticky'] = sticky

    async def remove(self, key: Key):
        logger.debug(f'remove()')
        with self._lock:
            self._records.pop(key, None)


if __name__ == '__main__':
    demo(LiveStreamView())
