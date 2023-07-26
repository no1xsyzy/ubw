#!/usr/bin/env python
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
        derive_uids: bool = True,
        derive_regex: bool = True,
):
    from ublcli.strange_stalker import StrangeStalkerHandler
    if regex is None:
        regex = []
    if uids is None:
        uids = []
    if derive_uids:
        from bilibili import get_info_by_room
        uids.extend(await asyncio.gather(*(get_info_by_room(room) for room in rooms)))
    if derive_regex:
        regex.extend(map(str, uids))
        regex.extend(map(str, rooms))
    regex = '|'.join(regex)
    return await listen_to_all(rooms, StrangeStalkerHandler(uids=uids, reg=regex))


@app.command('p')
@app.command('danmakup')
@sync
async def danmakup(rooms: list[int]):
    from ublcli.danmakup import DanmakuPHandler
    await listen_to_all(rooms, DanmakuPHandler())


@app.command('pian')
@sync
async def pian(rooms: list[int]):
    from .wocpian import PianHandler
    await listen_to_all(rooms, PianHandler())


@app.command('bhashm')
@sync
async def bhashm(rooms: list[int], famous_people: Annotated[list[int], typer.Option("--famous", "-f")] = None):
    from .bhashm import HashMarkHandler, create_csv_writer

    await listen_to_all(
        rooms,
        handler_factory=lambda room_id: HashMarkHandler(famous_people=famous_people,
                                                        csv_queue=create_csv_writer(room_id))
    )


@app.command('dump_raw')
@sync
async def dump_raw(rooms: list[int]):
    from .dump_raw import DumpRawHandler
    await listen_to_all(rooms, handler_factory=lambda r: DumpRawHandler(room_id=r))


@app.command('saver')
@app.command('s')
@sync
async def saver(rooms: list[int]):
    from .saver import SaverHandler
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
):
    main.config = config = load_config(cd)
    if log:
        init_logging(config)
    if sentry:
        init_sentry(config)
