import asyncio
import os
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Callable, Any

import typer

from .utils import sync, listen_to_all, Application

app = typer.Typer()


def init_sentry(cd):
    import sentry_sdk
    sentry_sdk.init(**cd['sentry'])


def init_logging(cd):
    import logging.config
    logging.config.dictConfig(cd['logging'])


def load_config(c: Path):
    import toml
    with c.open(encoding='utf-8') as f:
        return toml.load(f)


@app.command('ss')
@app.command('strange_stalker')
@sync
async def strange_stalker(
        rooms: Annotated[list[int], typer.Argument(help="")],
        regex: Annotated[list[str], typer.Option("--regex", "-r")] = None,
        uids: Annotated[list[int], typer.Option("--uids", "-u")] = None,
        ignore_danmaku: Annotated[list[int], typer.Option("--ignore", "-i")] = None,
        derive_uids: bool = True,
        derive_regex: bool = True,
):
    from .handlers import StrangeStalkerHandler
    if regex is None:
        regex = []
    if uids is None:
        uids = []
    if ignore_danmaku is None:
        ignore_danmaku = []
    if derive_uids:
        from .clients import BilibiliUnauthorizedClient
        async with BilibiliUnauthorizedClient() as client:
            uids.extend([i.room_info.uid
                         for i in await asyncio.gather(*(client.get_info_by_room(room)
                                                         for room in rooms))])
    if derive_regex:
        regex.extend(map(str, uids))
        regex.extend(map(str, rooms))
    regex = '|'.join(regex)
    ignore_danmaku = '|'.join(ignore_danmaku)
    return await listen_to_all(rooms, StrangeStalkerHandler(uids=uids, regex=regex, ignore_danmaku=ignore_danmaku))


@app.command('p')
@app.command('danmakup')
@sync
async def danmakup(
        rooms: list[int],
        ignore_danmaku: Annotated[list[str], typer.Option("--ignore", "-i")] = None,
        ignore_rate: float = 0.,
        dim_rate: float = .25,
        show_interact_word: bool = False,
        test_flags: str = "",
):
    from .handlers import DanmakuPHandler
    if ignore_danmaku:
        ignore_danmaku = '|'.join(ignore_danmaku)
    else:
        ignore_danmaku = None

    settings = {
        'ignore_danmaku': ignore_danmaku,
        'ignore_rate': ignore_rate,
        'dim_rate': dim_rate,
        'show_interact_word': show_interact_word,
        'test_flags': test_flags,
    }

    if 'use_ui' in test_flags:
        from .ui import LiveUI
        ui = LiveUI(alternate_screen=True)
        handler = DanmakuPHandler(**settings, ui=ui)
        with ui:
            await listen_to_all(rooms, handler)
    else:
        handler = DanmakuPHandler(**settings)
        await listen_to_all(rooms, handler)


@app.command('pian')
@sync
async def pian(rooms: list[int]):
    from .handlers import PianHandler
    await listen_to_all(rooms, PianHandler())


@app.command('bhashm')
@sync
async def bhashm(rooms: list[int], famous_people: Annotated[list[int], typer.Option("--famous", "-f")] = None):
    from .handlers import HashMarkHandler
    await listen_to_all(rooms, HashMarkHandler(famous_people=famous_people))


@app.command('dump_raw')
@sync
async def dump_raw(rooms: list[int]):
    from .handlers import DumpRawHandler
    await listen_to_all(rooms, handler_factory=lambda r: DumpRawHandler(room_id=r))


@app.command('saver')
@app.command('s')
@sync
async def saver(rooms: list[int]):
    from .handlers import SaverHandler
    await listen_to_all(rooms, handler_factory=lambda r: SaverHandler(room_id=r))


@app.command('living_status')
@app.command('w')
@sync
async def living_status(
        rooms: list[int] = (),
        from_user: Annotated[list[int], typer.Option("--from-user", "-u")] = (),
        from_dynamic: Annotated[list[int], typer.Option("--from-dynamic", "-d")] = (),
):
    from pydantic import TypeAdapter
    from .clients.bilibili import BilibiliClient
    from .handlers import LivingStatusHandler
    from . import models

    from_user = set(from_user)
    from_dynamic = set(from_dynamic)
    rooms = set(rooms)

    async with TypeAdapter(BilibiliClient).validate_python(main.config['accounts']['default']) as c:
        c: BilibiliClient
        for d in from_dynamic:
            f: models.Dynamic = await c.get_dynamic(d, features=('itemOpusStyle',))
            for t in f.item.module_dynamic.rich_text_nodes:
                if isinstance(t, models.bilibili.RichTextNodeTypeAt):
                    from_user.add(t.rid)

        for m in from_user:
            acc = await c.get_account_info(m)
            rooms.add(acc.live_room_id)

        await listen_to_all(list(rooms), LivingStatusHandler(), b_client=c)


@app.command('run')
@app.command('r')
@sync
async def run(cc: list[str]):
    coroutines = []
    for c in cc:
        match c.split('.'):
            case ['strange_stalker' | 'ss', k]:
                coroutines.append(strange_stalker.__wrapped__(**main.config['strange_stalker'][k]))
            case ['danmakup' | 'p', k]:
                coroutines.append(danmakup.__wrapped__(**main.config['danmakup'][k]))
            case ['pian', k]:
                coroutines.append(pian.__wrapped__(**main.config['pian'][k]))
            case ['bhashm' | 'h', k]:
                coroutines.append(bhashm.__wrapped__(**main.config['bhashm'][k]))
            case ['dump_raw' | 'd', k]:
                coroutines.append(dump_raw.__wrapped__(**main.config['dump_raw'][k]))
            case ['saver' | 's', k]:
                coroutines.append(saver.__wrapped__(**main.config['saver'][k]))
            case _:
                print(f"unknown mod {c}, skipped")
    await asyncio.gather(*coroutines)


@app.command('app_show')
@sync
async def app_show(app_name: str):
    application = Application.model_validate(main.config['apps'].get(app_name))
    from rich.pretty import pprint
    pprint(application)
    return application


@app.command('app_run')
@sync
async def app_run(app_name: str):
    application = Application.model_validate(main.config['apps'].get(app_name))
    try:
        return await application.run()
    finally:
        await application.close()


class _OutputChoice(str, Enum):
    url_only = 'url_only'
    info_link = 'info_link'
    info_link_url = 'info_link_url'
    tsv = 'tsv'
    m3u = 'm3u'
    raw = 'raw'
    raw_pretty = 'raw_pretty'
    analyzer = 'analyzer'
    libmpv = 'libmpv'


def extend_urlinfo(stream, fmt, cdc, url_info, real_original):
    host = url_info.host.replace('https://', '')
    url = f"{url_info.host}{cdc.base_url}{url_info.extra}"
    compressed = re.search(r"(\d+)_(?:minihevc|prohevc|bluray)", url)
    if compressed:
        info = f"C|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}"
    else:
        info = f"A|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}"
    yield url, info
    if real_original:
        if stream.protocol_name == 'http_stream':
            return  # seems unsupported
        if compressed:
            yield (re.sub(r"(\d+)_(?:minihevc|prohevc|bluray)", r'\1', url),
                   f"T|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}")


@app.command()
@sync
async def get_play_url(room_id: int,
                       output: _OutputChoice = _OutputChoice.info_link,
                       qn: int = 10000,
                       filter_protocol: str = '',
                       filter_format: str = '',
                       filter_codec: str = '',
                       print_first: bool = False,
                       real_original: bool = True,
                       ):
    from rich import get_console
    from rich.text import Text
    from .models.bilibili import RoomPlayInfo
    from .clients.bilibili import BilibiliCookieClient

    console = get_console()
    async with BilibiliCookieClient(**main.config['accounts']['default']) as client:
        play_info = await client.get_room_play_info(room_id, qn)

    each: Callable[[str, str], Any] | None = None
    after: Callable[[], Any] | None = None
    empty: Callable[[], Any] | None

    def empty():
        print(f'Play info of room {room_id} is empty or filtered', file=sys.stderr)

    match output:
        case _OutputChoice.raw:
            print(play_info.json())

        case _OutputChoice.raw_pretty:
            from rich.pretty import pprint
            pprint(play_info)

        case _OutputChoice.info_link:
            def each(url, info):
                console.print(Text(info), style=f"link {url}")

        case _OutputChoice.info_link_url:
            def each(url, info):
                console.print(Text(f"{info}\t{url}"), style=f"link {url}")

        case _OutputChoice.url_only:
            def each(url, info):
                print(url)

        case _OutputChoice.tsv:
            def each(url, info):
                print('\t'.join([info, *info[1:-1].split("|"), "", url]))

        case _OutputChoice.m3u:
            from itertools import count
            print("#EXTM3U")
            s = count()

            def each(url, info):
                print(f"#EXTINF:,[{next(s)}]{info}\n{url}\n")

        case _OutputChoice.libmpv:
            # experimental
            os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
            import mpv

            mpv_configs = main.config.get('mpv_configs', {})

            player = mpv.MPV(
                ytdl=True,
                input_default_bindings=True, input_vo_keyboard=True, osc=True, osd_font_size=35,
                **mpv_configs,
            )

            def each(url, info):
                print(info, url)
                player.loadfile(url, 'append-play', title=info, force_media_title=info)

            def after():
                player.wait_for_shutdown()

        case _OutputChoice.analyzer:
            from urllib.parse import urlparse
            columns = set()
            records = []

            def each(url, info):
                scheme, netloc, path, _, query, _ = urlparse(url)
                r = {'Name': info, 'Host': netloc, 'Url': url}
                for p in query.split('&'):
                    a, b = p.split('=')
                    if a not in columns:
                        columns.add(a)
                    r[a] = b
                records.append(r)

            def after():
                import csv
                writer = csv.DictWriter(sys.stdout, fieldnames=('Name', 'Host', 'Url', *sorted(columns)))
                writer.writeheader()
                writer.writerows(records)

        case _:
            raise NotImplementedError(f'{output} is not implemented')

    if callable(each):
        each_is_called = False
        if play_info.playurl_info is not None:
            for stream in play_info.playurl_info.playurl.stream:
                if filter_protocol != '' and stream.protocol_name not in filter_protocol:
                    continue
                for fmt in stream.format:
                    if filter_format != '' and fmt.format_name not in filter_format:
                        continue
                    for cdc in fmt.codec:
                        if qn != cdc.current_qn:
                            continue
                        if filter_codec != '' and cdc.codec_name not in filter_codec:
                            continue
                        for url_info in cdc.url_info:
                            for u, i in extend_urlinfo(stream, fmt, cdc, url_info, real_original):
                                each_is_called = True
                                each(u, i)
                                if print_first:  # should remove?
                                    return
        if not each_is_called and empty is not None:
            empty()

    if callable(after):
        after()


@app.command()
def print_config():
    from rich import print
    print(main.config)


@app.callback()
def main(
        cd: Annotated[Path, typer.Option('--config', '-c')] = "config.toml",
        sentry: bool = True,
        log: bool = True,
        verbose: Annotated[int, typer.Option('--verbose', '-v', count=True)] = 0,
        remote_debug_with_port: int = 0,
        config_override: list[str] = (),
):
    cd = Path(cd)
    main.config = config = load_config(cd)
    if log:
        if verbose > 0:
            config['logging']['root']['level'] = 'DEBUG'
            config['logging']['root']['handlers'] = ['richconsole']
        init_logging(config)
    if config_override is not None:
        for c in config_override:
            ks, v = c.split("=", 1)
            from ast import literal_eval
            v = literal_eval(v)
            p = config
            *kk, lk = ks.split('.')
            for k in kk:
                if k in p:
                    p = p[k]
                else:
                    break
            else:
                p[lk] = v
    if sentry:
        init_sentry(config)
    if 0 < remote_debug_with_port < 65536:
        import pdb_attach
        pdb_attach.listen(remote_debug_with_port)
