import asyncio
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
        dim_rate: float = .2,
        use_ui: bool = False,
        show_interact_word: bool = False,
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
):
    main.config = config = load_config(cd)
    if log:
        if verbose > 0:
            config['logging']['root']['level'] = 'DEBUG'
        init_logging(config)
    if sentry:
        init_sentry(config)
