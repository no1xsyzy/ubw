import asyncio
import logging
import sys

import toml
from rich.logging import RichHandler

import blivedm
from .handler import BliveTinyFluxHandler


async def listen_to_all(room_ids: list[int]):
    clients = []
    for room_id in room_ids:
        client = blivedm.BLiveClient(room_id)
        handler = BliveTinyFluxHandler(room_id=room_id)
        client.add_handler(handler)
        client.start()
        clients.append(client)

    try:
        await asyncio.gather(*(client.join() for client in clients))
    finally:
        await asyncio.gather(*(client.stop_and_close() for client in clients))


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            tracebacks_suppress=['logging', 'rich', 'tinydb'],
            show_path=False,
        )],
    )

    argi = iter(sys.argv)

    _ = next(argi)

    room_ids = []

    for arg in argi:
        if arg in ['-c', '--config']:
            with open(next(argi), 'r') as f:
                cfg = toml.load(f)
                room_ids = cfg['room_ids']
        elif arg in ['-r', '--room']:
            for room_id in (int(sri) for sri in next(argi).split(",")):
                if room_id < 0:
                    room_ids.remove(-room_id)
                elif room_id not in room_ids:
                    room_ids.append(room_id)
        else:
            raise ValueError(f"unknown arg {arg}")
    if not room_ids:
        sys.exit("no room_ids, this may be due to a config mistake")

    try:
        asyncio.run(listen_to_all(room_ids))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
