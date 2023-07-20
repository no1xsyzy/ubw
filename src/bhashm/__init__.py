import asyncio
import logging
import sys

import sentry_sdk
from rich.logging import RichHandler

import blivedm
from .handler import HashMarkHandler, create_csv_writer

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
        asyncio.run(blivedm.listen_to_all(
            room_ids,
            handler_factory=lambda room_id: HashMarkHandler(famous_people=famous_people,
                                                            csv_queue=create_csv_writer(room_id))
        ))
    except KeyboardInterrupt:
        print("keyboard interrupt", file=sys.stdout)
