import asyncio
import logging
import sys

import toml
from rich.logging import RichHandler

from . import listen_to_all


def main():
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    argi = iter(sys.argv)

    _ = next(argi)

    room_ids = []
    famous_people = []

    for arg in argi:
        if arg in ['-c', '--config']:
            with open(next(argi), 'r') as f:
                cfg = toml.load(f)
                room_ids = cfg['room_ids']
                famous_people = cfg['famous_people']
        else:
            raise ValueError()
    if not room_ids:
        sys.exit("no room_ids, this may be due to a config mistake")

    try:
        asyncio.get_event_loop().run_until_complete(listen_to_all(room_ids, famous_people))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
