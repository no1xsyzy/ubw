import sys

import toml

from . import go_with


def go_with_argv():
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
        elif arg in ['-r', '--room']:
            for room_id in (int(sri) for sri in next(argi).split(",")):
                if room_id < 0:
                    room_ids.remove(-room_id)
                elif room_id not in room_ids:
                    room_ids.append(room_id)
        elif arg in ['-f', '--famous']:
            for fuid in (int(suid) for suid in next(argi).split(",")):
                if fuid < 0:
                    famous_people.remove(-fuid)
                elif fuid not in famous_people:
                    famous_people.append(fuid)
        else:
            raise ValueError()
    if not room_ids:
        sys.exit("no room_ids, this may be due to a config mistake")

    go_with(famous_people, room_ids)
