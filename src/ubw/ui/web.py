import itertools
import json
import logging
from functools import cached_property
from html import escape
from typing import Union

import aiohttp
from aiohttp import web

from ._base import *

logger = logging.getLogger('ubw.ui.web')

JR = Union[
    tuple[Literal['add'], str, str, str],
    tuple[Literal['edit'], str, str, str],
    tuple[Literal['del'], str],
    tuple[Literal['fs'], str],
]


class Web(StreamUI):
    uic: Literal['web'] = 'web'
    palette: list[str] = 'red,green,yellow,blue,magenta,cyan'.split(',')
    title: str = 'Web Stream UI'

    bind_host: str = 'localhost'
    bind_port: int = 8080

    cache_max_len: int = 20

    _runner: web.AppRunner | None = None
    _site: web.TCPSite | None = None
    _task: asyncio.Task | None = None

    @cached_property
    def cache(self) -> list[tuple[str, bool, str]]:
        return []

    def render_cache(self):
        return ''.join(f'<div id="{key}" class="{self.format_class(sticky)}">{s}</div>'
                       for key, sticky, s in self.cache)

    @cached_property
    def connected_ws(self) -> list[web.WebSocketResponse]:
        return []

    @cached_property
    def _queue(self):
        return asyncio.Queue()

    @cached_property
    def _s(self):
        return itertools.count()

    def color_of(self, text):
        return self.palette[hash(text) % len(self.palette)]

    def color_style(self, text):
        return f'color: {self.color_of(text)}'

    def color_class(self, text):
        return f'color-{hash(text) % len(self.palette)}'

    def color_css(self):
        return '\n'.join('.color-%d { color: %s; }' % (i, c) for i, c in enumerate(self.palette))

    def format_class(self, sticky: bool) -> str:
        if sticky:
            return 'sticky'
        else:
            return ''

    def format_record(self, record: Record) -> str:
        s = ""
        for seg in record.segments:
            match seg:
                case PlainText(text=text):
                    s = f'{s}{escape(text)}'
                case Anchor(text=text, href=href):
                    s = f'{s}<a href="{href}">{escape(text)}</a>'
                case User(name=name, uid=uid):
                    s = f'{s}<a href="https://space.bilibili.com/{uid}" ' \
                        f'class="{self.color_class(str(uid))}">{escape(name)}</a>'
                case Room(owner_name=name, room_id=room_id):
                    s = f'{s}<a href="https://live.bilibili.com/{room_id}">{escape(name)}的直播间</a>'
                case RoomTitle(title=title, room_id=room_id):
                    s = f'{s}<a href="https://live.bilibili.com/{room_id}">《{escape(title)}》</a>'
                case ColorSeeSee(text=text):
                    s = f'{s}<span class="{self.color_class(text)}">{escape(text)}</span>'
                case DebugInfo(text=text, info=info):
                    s = f'{s}<span class="debug-info" ' \
                        f'data-debug-info="{escape(json.dumps(info))}">({escape(text)})</span>'

        return s

    async def add_record(self, record: Record, sticky: bool = False):
        s = next(self._s)
        key = f"r{s}"
        s = self.format_record(record)
        klass = self.format_class(sticky)
        await self._queue.put(['add', key, klass, s])
        self.cache.append((key, sticky, s))
        if len(self.cache) > self.cache_max_len:
            self.cache.pop(0)
        return key

    async def edit_record(self, key, *, record=None, sticky=None):
        i = next(i for i, c in enumerate(self.cache) if c[0] == key)
        key, old_sticky, s = self.cache[i]
        if sticky is None:
            sticky = old_sticky
        klass = self.format_class(sticky)
        if record is not None:
            s = self.format_record(record)
        await self._queue.put(['edit', key, klass, s])
        self.cache[i] = key, sticky, s

    async def remove(self, key):
        await self._queue.put(['del', key])
        i = next(i for i, c in enumerate(self.cache) if c[0] == key)
        del self.cache[i]

    async def _main_task(self):
        while True:
            msg = await self._queue.get()
            logger.debug('ws send_json %s' % msg)
            for ws in self.connected_ws[:]:
                if not ws.closed:
                    try:
                        await ws.send_json(msg)
                    except Exception as e:
                        logger.exception('ws send_json exception %s' % e)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        await ws.send_json(['fs', self.render_cache()])
        self.connected_ws.append(ws)

        msg: aiohttp.WSMessage
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.ERROR:
                logger.exception('ws connection closed with exception', exc_info=ws.exception())
        self.connected_ws.remove(ws)

        return ws

    async def index_handler(self, request):
        script = """
const socket = new WebSocket("ws://localhost:8080/ws");

socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    const main = document.getElementById('main');
    const sticky = document.getElementById('sticky');
    
    const op = data[0]
    if (op === 'add') {
        let el = document.createElement('DIV');
        el.id = data[1];
        el.classList = data[2];
        el.innerHTML = data[3];
    } else if (op === 'edit') {
        let el = document.getElementById(data[1]);
        if (el === null) return;
        el.classList = data[2];
        el.innerHTML = data[3];
    } else if (op === 'del') {
        let el = document.getElementById(data[1]);
        if (el === null) return;
        el.remove();
    } else if (op === 'fs') {
        sticky.innerHTML = ""
        main.innerHTML = data[1];
    }
    
    for (let el of document.querySelectorAll("#sticky :not(.sticky)")){
        el.remove();
    }
    
    while (main.children.length > 20) {
        let el = main.children[0];
        if (el.classList.contains('sticky')){
            document.getElementById('sticky').appendChild(el)
        } else {
            el.remove();
        }
    }
});
"""
        text = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{self.title}</title>
    <script>{script}</script>
    <style>{self.color_css()}</style>
</head>
<body>

<div id="sticky"></div>
<div id="main">
{self.render_cache()}
</div>

</body>
</html>
"""
        return web.Response(body=text, headers={'content-type': 'text/html; chatset=utf-8'})

    @cached_property
    def app(self):
        app = web.Application()

        app.add_routes([
            web.get('/', self.index_handler),
            web.get('/ws', self.websocket_handler),
        ])
        return app

    async def start(self):
        self._task = asyncio.create_task(self._main_task())
        self._runner = runner = web.AppRunner(self.app)
        await runner.setup()
        self._site = site = web.TCPSite(runner, self.bind_host, self.bind_port)
        await site.start()
        logger.info('server started at http://{}:{}'.format(self.bind_host, self.bind_port))

    async def stop(self):
        self._task.cancel('stop')
        await self._site.stop()
        await self._runner.cleanup()


if __name__ == '__main__':
    demo(Web())
