import asyncio
import re
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from .utils import sync, listen_to_all

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
    from .handlers import StrangeStalkerHandler, StrangeStalkerHandlerSettings
    if regex is None:
        regex = []
    if uids is None:
        uids = []
    if ignore_danmaku is None:
        ignore_danmaku = []
    if derive_uids:
        from bilibili import get_info_by_room
        uids.extend([i.room_info.uid for i in await asyncio.gather(*(get_info_by_room(room) for room in rooms))])
    if derive_regex:
        regex.extend(map(str, uids))
        regex.extend(map(str, rooms))
    regex = '|'.join(regex)
    ignore_danmaku = '|'.join(ignore_danmaku)
    settings = StrangeStalkerHandlerSettings(uids=uids, regex=regex, ignore_danmaku=ignore_danmaku)
    return await listen_to_all(rooms, StrangeStalkerHandler(settings))


@app.command('p')
@app.command('danmakup')
@sync
async def danmakup(
        rooms: list[int],
        ignore_danmaku: Annotated[list[str], typer.Option("--ignore", "-i")] = None,
        ignore_rate: float = 0.,
        dim_rate: float = .25,
        use_ui: bool = False,
        show_interact_word: bool = False,
        test_flags: str = "",
):
    from .handlers import DanmakuPHandler, DanmakuPHandlerSettings
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

    if use_ui:
        from .ui import LiveUI
        ui = LiveUI(alternate_screen=True)
        handler = DanmakuPHandler(
            DanmakuPHandlerSettings(**settings, ui=ui))
        with ui:
            await listen_to_all(rooms, handler)
    else:
        handler = DanmakuPHandler(
            DanmakuPHandlerSettings(**settings))
        await listen_to_all(rooms, handler)


@app.command('pian')
@sync
async def pian(rooms: list[int]):
    from .handlers import PianHandler
    await listen_to_all(rooms, PianHandler())


@app.command('bhashm')
@sync
async def bhashm(rooms: list[int], famous_people: Annotated[list[int], typer.Option("--famous", "-f")] = None):
    from .handlers import HashMarkHandler, HashMarkHandlerSettings
    await listen_to_all(rooms, HashMarkHandler(HashMarkHandlerSettings(famous_people=famous_people)))


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


class _OutputChoice(str, Enum):
    url_only = 'url_only'
    info_link = 'info_link'
    info_link_url = 'info_link_url'
    tsv = 'tsv'
    m3u = 'm3u'
    raw = 'raw'
    raw_pretty = 'raw_pretty'
    analyzer = 'analyzer'


def extend_urlinfo(stream, fmt, cdc, url_info, real_original):
    host = url_info.host.replace('https://', '')
    url = f"{url_info.host}{cdc.base_url}{url_info.extra}"
    info = f"E|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}"
    yield url, info
    if real_original:
        if stream.protocol_name == 'http_stream':
            return  # seems unsupported
        if re.search(r"(\d+)_(?:minihevc|prohevc|bluray)", url):
            yield (re.sub(r"(\d+)_(?:minihevc|prohevc|bluray)", r'\1', url),
                   f"RO|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}")


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
    from bilibili import get_room_play_info, RoomPlayInfo
    from rich import get_console
    from rich.text import Text
    console = get_console()
    play_info: RoomPlayInfo = await get_room_play_info(room_id, qn)

    match output:
        case _OutputChoice.raw:
            print(play_info.json())
            each = None
            after = None

        case _OutputChoice.raw_pretty:
            from rich.pretty import pprint
            pprint(play_info)
            each = None
            after = None

        case _OutputChoice.info_link:
            def each(url, info):
                console.print(Text(info), style=f"link {url}")

            after = None

        case _OutputChoice.info_link_url:
            def each(url, info):
                console.print(Text(f"{info}\t{url}"), style=f"link {url}")

            after = None

        case _OutputChoice.url_only:
            def each(url, info):
                print(url)

            after = None

        case _OutputChoice.tsv:
            def each(url, info):
                print('\t'.join([info, *info[1:-1].split("|"), "", url]))

            after = None

        case _OutputChoice.m3u:
            from itertools import count
            print("#EXTM3U")
            s = count()

            def each(url, info):
                print(f"#EXTINF:,[{next(s)}]{info}\n{url}\n")

            after = None

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
        if play_info.playurl_info is None:
            print(f'No Play Info for room {room_id}', file=sys.stderr)
        else:
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
                                each(u, i)
                                if print_first:  # should remove?
                                    return

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
):
    main.config = config = load_config(cd)
    if log:
        if verbose > 0:
            config['logging']['root']['level'] = 'DEBUG'
        init_logging(config)
    if sentry:
        init_sentry(config)
    if 0 < remote_debug_with_port < 65536:
        import pdb_attach
        pdb_attach.listen(remote_debug_with_port)
