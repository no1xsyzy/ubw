import importlib.util
import os
import sys
from collections import namedtuple
from pathlib import Path

import platformdirs

Paths = namedtuple('paths', ['config_path', 'cache_path', 'data_path'])


def get_path(
        *,
        cmdline_config_path: Path | None = None,
        cmdline_data_path: Path | None = None,
        cmdline_cache_path: Path | None = None,
        ensure_exists: bool = True,
) -> tuple[Path, Path, Path]:
    config_path = cmdline_config_path
    data_path = cmdline_data_path
    cache_path = cmdline_cache_path

    if config_path is None and (p := os.getenv('UBW_CONFIG_DIR')):
        config_path = Path(p).resolve()
    if data_path is None and (p := os.getenv('UBW_DATA_DIR')):
        data_path = Path(p).resolve()
    if cache_path is None and (p := os.getenv('UBW_CACHE_DIR')):
        cache_path = Path(p).resolve()

    is_frozen = getattr(sys, "frozen", False)
    if is_frozen:
        root = Path(sys.executable).parent
    else:
        spec = importlib.util.find_spec('ubw')
        root = Path(
            spec.origin).resolve().parent.parent.parent if spec is not None and spec.origin is not None else None

    if root is not None and (root / '.portable').exists():  # is portable
        if config_path is None:
            config_path = root
        if data_path is None:
            data_path = root / 'ubw_data'
        if cache_path is None:
            cache_path = root / 'ubw_cache'
    else:
        if config_path is None:
            config_path = platformdirs.user_config_path(
                appname='ubw', roaming=True).resolve()
        if data_path is None:
            data_path = platformdirs.user_data_path(
                appname='ubw', roaming=True).resolve()
        if cache_path is None:
            cache_path = platformdirs.user_cache_path(
                appname='ubw').resolve()

    if ensure_exists:
        config_path.mkdir(parents=True, exist_ok=True)
        data_path.mkdir(parents=True, exist_ok=True)
        cache_path.mkdir(parents=True, exist_ok=True)

    return Paths(config_path, cache_path, data_path)
