import asyncio
import logging
import sys

import sentry_sdk
from rich.logging import RichHandler

from bhashm.handler import listen_to_all

sentry_sdk.init(
    dsn="https://f6bcb89a35fb438f81eb2d7679c5ded0@o4504791466835968.ingest.sentry.io/4504791473127424",
    traces_sample_rate=1.0,
)


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
