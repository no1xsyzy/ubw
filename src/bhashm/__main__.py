import asyncio
import sys

import toml

from . import listen_to_all

argi = iter(sys.argv)

cmd = next(argi)

config = None
room_ids = []
famous_people = []

for arg in argi:
    if arg in ['-c', '--config']:
        config = next(argi)
    else:
        raise ValueError()
if config is None:
    config = "config.example.toml"
with open(config, 'r') as f:
    cfg = toml.load(f)
    room_ids = cfg['room_ids']
    famous_people = cfg['famous_people']

try:
    asyncio.get_event_loop().run_until_complete(listen_to_all(room_ids, famous_people))
except KeyboardInterrupt:
    print("keyboard interrupt", file=sys.stdout)
