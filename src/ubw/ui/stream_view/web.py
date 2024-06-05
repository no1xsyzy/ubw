import asyncio
import itertools
import json
import logging
from functools import cached_property
from typing import Union, NamedTuple

import aiohttp
import lxml
from aiohttp import web
from lxml.html.builder import HTML, BODY, HEAD, DIV, META, TITLE, SCRIPT, STYLE, SPAN, A, IMG, ATTR, CLASS, BR

from ._base import *

logger = logging.getLogger('ubw.stream_view.web')

JR = Union[
    tuple[Literal['add'], str, str, str],
    tuple[Literal['edit'], str, str, str],
    tuple[Literal['del'], str],
    tuple[Literal['fs'], str],
]


class Formatted(NamedTuple):
    key: str
    sticky: bool
    element: lxml.html.HtmlElement


class Web(BaseStreamView):
    uic: Literal['web'] = 'web'
    palette: list[str] = ["red", "green", "blue", "magenta"]
    title: str = 'Web Stream UI'

    show_date: bool = True

    bind_host: str = 'localhost'
    bind_port: int = 8080

    cache_max_len: int = 20

    _runner: web.AppRunner | None = None
    _site: web.TCPSite | None = None
    _task: asyncio.Task | None = None

    @cached_property
    def cache_sticky(self) -> list[Formatted]:
        return []

    @cached_property
    def cache(self) -> list[Formatted]:
        return []

    def render_body(self):
        return BODY(
            DIV({'id': 'sticky'},
                *(DIV({'id': key, 'class': self.format_class(sticky)}, s)
                  for key, sticky, s in self.cache_sticky)),
            DIV({'id': 'main'},
                *(DIV({'id': key, 'class': self.format_class(sticky)}, s)
                  for key, sticky, s in self.cache)))

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

    def format_record(self, record: Record) -> lxml.html.HtmlElement:
        if self.show_date:
            h = [SPAN({'class': 'datetime'}, record.time.astimezone().strftime('[%Y-%m-%d %H:%M:%S] '))]
        else:
            h = []
        for seg in record.segments:
            match seg:
                case PlainText(text=text):
                    h.append(text)
                case Anchor(text=text, href=href):
                    h.append(
                        A(ATTR(href=href),
                          text))
                case User(name=name, uid=uid, face=face):
                    if face == '':
                        h.append(
                            A(ATTR(href=f"https://space.bilibili.com/{uid}", target='_blank'),
                              CLASS(self.color_class(str(uid))),
                              name))
                    else:
                        h.append(
                            A(ATTR(href=f"https://space.bilibili.com/{uid}", target='_blank'),
                              CLASS(self.color_class(str(uid))),
                              IMG(src=face, style="height: 1em; width: 1em; border-radius: 0.5em;"),
                              name))
                case Room(owner_name=name, room_id=room_id):
                    h.append(
                        A(ATTR(href=f"https://live.bilibili.com/{room_id}", target='_blank'),
                          f"{name}的直播间"))
                case RoomTitle(title=title, room_id=room_id):
                    h.append(
                        A(ATTR(href=f"https://live.bilibili.com/{room_id}", target='_blank'), CLASS('room'),
                          f"《{title}》"))
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
                            SPAN(CLASS('currency'),
                                 f" [{mark}{price}]"))
                case Picture(url=url, alt=alt):
                    h.append(IMG(CLASS('picture'), src=url, alt=alt, title=alt))
                case LineBreak():
                    h.append(BR())
                case Emoji(codepoint=cp):
                    h.append(
                        SPAN(CLASS('emoji'),
                             f"{cp}\N{VS16}"))
        return SPAN(*h)

    def find_key(self, key):
        for i, c in enumerate(self.cache_sticky):
            if c[0] == key:
                return self.cache_sticky, i
        for i, c in enumerate(self.cache):
            if c[0] == key:
                return self.cache, i
        return None, None

    async def add_record(self, record: Record, sticky: bool = False):
        key = f"r{next(self._s)}"
        s = self.format_record(record)
        klass = self.format_class(sticky)
        await self._queue.put(('add', key, klass, lxml.html.tostring(s, encoding='unicode')))
        self.cache.append(Formatted(key, sticky, s))

        if len(self.cache) > self.cache_max_len:
            g = self.cache.pop(0)
            if g.sticky:
                self.cache_sticky.append(g)

        return key

    async def edit_record(self, key, *, record=None, sticky=None):
        cache, i = self.find_key(key)
        key, old_sticky, s = cache[i]
        if sticky is None:
            sticky = old_sticky
        if record is not None:
            s = self.format_record(record)
        if sticky is False and cache is self.cache_sticky:
            del cache[i]
            await self._queue.put(('del', key))
        cache[i] = Formatted(key, sticky, s)
        klass = self.format_class(sticky)
        await self._queue.put(('edit', key, klass, lxml.html.tostring(s, encoding='unicode')))

    async def remove(self, key):
        await self._queue.put(('del', key))
        cache, i = self.find_key(key)
        del cache[i]

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
        await ws.send_json(('fs', lxml.html.tostring(self.render_body(), encoding='unicode')))
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
        body.innerHTML = data[1];
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

        style = """
/* reset */
html { box-sizing: border-box; }
*, *:before, *:after { box-sizing: inherit; }
html { -moz-text-size-adjust: none; -webkit-text-size-adjust: none; text-size-adjust: none; }
body, h1, h2, h3, h4, p,
figure, blockquote, dl, dd { margin: 0; }
ul[role='list'], ol[role='list'] { list-style: none; }
ul[class], ol[class] { margin: 0; padding: 0; list-style: none; }
body { min-height: 100vh; line-height: 1.5; }
h1, h2, h3, h4, button, input, label { line-height: 1.1; }
h1, h2, h3, h4 { text-wrap: balance; }
a:not([class]) { text-decoration-skip-ink: auto; color: currentColor; }
input, button, textarea, select { font: inherit; }
textarea:not([rows]) { min-height: 10em; }
:target { scroll-margin-block: 5ex; }
/* end of reset */

span.datetime { color: darkcyan; }
span.debug-info { color: orange; }
.picture { max-width: 50%; }
@media screen and (max-width: 600px) { .picture { max-width: 100%; } }
"""

        body = lxml.html.tostring(
            HTML(
                HEAD(
                    META(charset='UTF-8'),
                    TITLE(self.title),
                    SCRIPT(script),
                    STYLE(self.color_css()),
                    STYLE(style),
                ),
                self.render_body()
            ),
            encoding='unicode',
            pretty_print=True,
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
        task = self._task
        self._task = None
        task.cancel('stop')
        try:
            await task
        except asyncio.CancelledError:
            pass
        for ws in self.connected_ws:
            await ws.close()
        await self._site.stop()
        await self._runner.cleanup()


if __name__ == '__main__':
    demo(Web())
