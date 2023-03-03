import asyncio
import logging
import sys

from rich.logging import RichHandler

from bhashm.handler import listen_to_all


def go_with(famous_people, room_ids):
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[RichHandler(
            # rich_tracebacks=True,
            # tracebacks_show_locals=True,
            tracebacks_suppress=['logging', 'rich'],
            show_path=False,
        )],
    )

    try:
        asyncio.run(listen_to_all(room_ids, famous_people))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
