import functools
import logging
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import aiofiles
import platformdirs
from aiotinydb import AIOTinyDB, AIOJSONStorage
from aiotinydb.middleware import AIOMiddleware
from tinydb_serialization import SerializationMiddleware as _SyncSerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer, Serializer


class TimeDeltaSerializer(Serializer):
    OBJ_CLASS = timedelta

    def encode(self, obj):
        return str(obj.total_seconds())

    def decode(self, s):
        return timedelta(seconds=float(s))


class SerializationMiddleware(_SyncSerializationMiddleware, AIOMiddleware):
    pass


logger = logging.getLogger('userdata')


def get_path():
    env = os.environ.get('UBW_ROOT', default=None)
    if env:
        return Path(env) / 'ubw_data'

    import sys
    main = Path(sys.argv[0]).resolve()
    print(f'{main = }')
    print(f'{[*main.parents] = }')
    print(f'{sys.prefix = }')
    if main.name == '__main__.py':
        portable_root = main.parent.parent.parent
    else:
        if Path(sys.prefix) in main.parents:
            portable_root = Path.cwd().resolve()
        else:
            portable_root = main.parent

    if os.environ.get('UBW_PORTABLE') or (portable_root / '.portable').is_file():
        return portable_root / 'ubw_data', portable_root

    return (Path(platformdirs.user_data_dir('ubw', roaming=True)).resolve(),
            Path(platformdirs.user_config_dir('ubw', roaming=True)).resolve())


user_data_path, user_config_path = get_path()
user_data_path.mkdir(parents=True, exist_ok=True)
user_config_path.mkdir(parents=True, exist_ok=True)


@functools.cache
def get_absolute_database(absolute_path: Path):
    assert absolute_path.is_absolute()
    serialization = SerializationMiddleware(AIOJSONStorage)
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    serialization.register_serializer(TimeDeltaSerializer(), 'timedelta')
    db = AIOTinyDB(str(absolute_path), storage=serialization)
    return db


def get_tiny_database(db):
    path = (user_data_path / f'{db}.tinydb').resolve()
    return get_absolute_database(path)


@asynccontextmanager
async def tiny_database(db):
    db = get_tiny_database(db)
    async with db:
        yield db


def get_toml(fn='config'):
    path = (user_config_path / f'{fn}.toml').resolve()
    import toml
    try:
        with path.open() as f:
            return toml.load(f)
    except FileNotFoundError:
        return {}


@asynccontextmanager
async def modify_toml(fn='config'):
    path = (user_config_path / f'{fn}.toml').resolve()
    swap_path = (user_config_path / f'{fn}.toml.swp').resolve()
    import toml

    # use swap as lock
    async with aiofiles.open(swap_path, 'w') as swap:
        async with aiofiles.open(path) as f:
            s = await f.read()
            data = toml.loads(s)
        try:
            yield data
        except Exception:
            logger.error("Exception occurs when modifying toml, abort write back")
            raise
        s_out = toml.dumps(data)
        await swap.write(s_out)
    swap_path.replace(path)
