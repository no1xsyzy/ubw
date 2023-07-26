#!/usr/bin/env python
import asyncio
from pathlib import Path
from typing import Annotated

import typer

import blivedm

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
def strange_stalker(c: str, cd: Annotated[Path, typer.Option('--config', '-c')] = "config.toml"):
    from strange_stalker import main
    config = load_config(cd)
    init_logging(config)
    init_sentry(config)
    main(**config['strange_stalker'][c])


@app.command('run')
@blivedm.sync
async def run(cc: list[str], cd: Annotated[Path, typer.Option('--config', '-c')] = "config.toml"):
    config = load_config(cd)
    init_logging(config)
    init_sentry(config)
    coroutines = []
    for c in cc:
        mod, k = c.split('.', 2)
        match mod:
            case 'strange_stalker' | 'ss':
                from strange_stalker import main
                coroutines.append(main.__wrapped__(**config['strange_stalker'][k]))
            case _:
                print(f"unknown mod {mod}, skipped")
    await asyncio.gather(*coroutines)


@app.command()
def print_config(cd: Annotated[Path, typer.Option('--config', '-c')] = "config.toml"):
    config = load_config(cd)
    from rich import print
    print(config)


if __name__ == '__main__':
    app()
