import random
import string
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from unittest.mock import patch

import ubw


def generate_random_string(mark=None):
    tok = ''.join(random.choices(string.ascii_letters, k=16))
    if mark is None:
        return tok
    return f"<{mark}.{tok}>"


def test_call_by_module():
    with Popen([sys.executable, '-m', 'ubw', '--help'], stdout=PIPE, text=True) as proc:
        out = proc.stdout.read()
    assert out.strip().startswith('Usage: python -m ubw [OPTIONS] COMMAND [ARGS]...')


def test_init_sentry():
    s = generate_random_string()
    with patch('sentry_sdk.init') as mock:
        ubw.init_sentry({'sentry': {'magic': 'dict', 'string': s}})
        mock.assert_called_once_with(magic='dict', string=s)


def test_init_logging():
    s = generate_random_string()
    with patch('logging.config.dictConfig') as mock:
        ubw.init_logging({'logging': {'magic': 'dict', 'string': s}})
        mock.assert_called_once_with({'magic': 'dict', 'string': s})


def test_config(tmp_path):
    config_path: Path = tmp_path / 'config.toml'
    s = generate_random_string()
    with config_path.open('wt', encoding='utf-8') as f:
        f.writelines([
            '[config]\n',
            'magic="' + s + '"\n',
        ])
    ret = ubw.load_config(config_path)
    assert ret == {'config': {'magic': s}}
