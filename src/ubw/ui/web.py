import asyncio
import itertools
import json
import logging
from functools import cached_property
from typing import Union

import aiohttp
import lxml
from aiohttp import web
from lxml.html.builder import HTML, BODY, HEAD, DIV, META, TITLE, SCRIPT, STYLE, SPAN, A, IMG, ATTR, CLASS

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
    palette: list[str] = ["red", "green", "blue", "magenta"]
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
        return asyncio.Queue[JR]()

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
        h = []
        for seg in record.segments:
            match seg:
                case PlainText(text=text):
                    h.append(text)
                case Anchor(text=text, href=href):
                    h.append(A({'href': href}, text))
                case User(name=name, uid=uid, face=face):
                    if face == '':
                        h.append(
                            A({'href': f"https://space.bilibili.com/{uid}", 'class': self.color_class(str(uid))},
                              name))
                    else:
                        h.append(
                            A({'href': f"https://space.bilibili.com/{uid}", 'class': self.color_class(str(uid))},
                              IMG(src=face, style="height: 1em; width: 1em; border-radius: 0.5em;"),
                              name))
                case Room(owner_name=name, room_id=room_id):
                    h.append(
                        A(ATTR(href=f"https://live.bilibili.com/{room_id}"), f"{name}的直播间"))
                case RoomTitle(title=title, room_id=room_id):
                    h.append(
                        A(ATTR(href=f"https://live.bilibili.com/{room_id}"), f"《{title}》"))
                case ColorSeeSee(text=text):
                    h.append(
                        SPAN(CLASS(self.color_class(text)),
                             text))
                case DebugInfo(text=text, info=info):
                    h.append(
                        SPAN(CLASS('debug-info'), {'data-debug-info': json.dumps(info)},
                             text))
                case Currency(price=price, mark=mark):
                    if price > 0:
                        h.append(
                            SPAN(CLASS('currency'), f" [{mark}{price}]"))
                case Picture(url=url, alt=alt):
                    h.append(IMG(src=url, alt=alt))
        return lxml.html.tostring(SPAN(*h), encoding='unicode')

    async def add_record(self, record: Record, sticky: bool = False):
        s = next(self._s)
        key = f"r{s}"
        s = self.format_record(record)
        klass = self.format_class(sticky)
        await self._queue.put(('add', key, klass, s))
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
        await self._queue.put(('edit', key, klass, s))
        self.cache[i] = key, sticky, s

    async def remove(self, key):
        await self._queue.put(('del', key))
        i = next(i for i, c in enumerate(self.cache) if c[0] == key)
        del self.cache[i]

    async def _main_task(self):
        while True:
            msg = await self._queue.get()
            logger.debug(f'ws send_json {msg=}')
            for ws in self.connected_ws[:]:
                if not ws.closed:
                    try:
                        await ws.send_json(msg)
                    except Exception as e:
                        logger.exception('ws send_json exception', exc_info=e)

    async def websocket_handler(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        logger.info("ws connection from {}".format(request.get_extra_info('peername')))
        await ws.send_json(('fs', self.render_cache()))
        self.connected_ws.append(ws)

        msg: aiohttp.WSMessage
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.ERROR:
                logger.exception('ws connection closed with exception', exc_info=ws.exception())
                continue
            logger.warning('ws received information from client but not understand, ignored')
        self.connected_ws.remove(ws)
        await ws.close()

        return ws

    async def index_handler(self, request: web.Request):
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
        main.appendChild(el);
    } else if (op === 'edit') {
        let el = document.getElementById(data[1]);
        if (el === null) return;
        if (el.parentElement === sticky && data[2] !== 'sticky') { el.remove(); return; } 
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
            sticky.appendChild(el)
        } else {
            el.remove();
        }
    }
});
"""

        body = lxml.html.tostring(
            HTML(
                HEAD(
                    META(charset='UTF-8'),
                    TITLE(self.title),
                    SCRIPT(script),
                    STYLE(self.color_css()),
                ),
                BODY(
                    DIV(id='sticky'),
                    lxml.html.fromstring(f'<div id="main">{self.render_cache()}</div>'),
                ),
            )
        )
        return web.Response(body=body, headers={'content-type': 'text/html; chatset=utf-8'})

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
