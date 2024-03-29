import random
import string
import sys
from pathlib import Path
from subprocess import Popen, PIPE
from unittest.mock import patch

from typer.testing import CliRunner

import ubw

runner = CliRunner()


def generate_random_string(mark=None):
    tok = ''.join(random.choices(string.ascii_letters, k=16))
    if mark is None:
        return tok
    return f"<{mark}.{tok}>"


def test_call_by_module():
    with Popen([sys.executable, '-m', 'ubw', '--help'], stdout=PIPE, text=True, encoding='utf-8') as proc:
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


def test_print_config():
    config_path = generate_random_string()
    config = {}
    with patch('ubw.load_config') as p_load:
        p_load.return_value = config
        with patch('ubw.init_logging') as p_log:
            with patch('ubw.init_sentry') as p_sentry:
                result = runner.invoke(ubw.app, ['--config', config_path, 'print-config'])
                p_load.assert_called_once_with(Path(config_path))
                p_log.assert_called_once_with(config)
                p_sentry.assert_called_once_with(config)
    assert result.exit_code == 0
    assert result.stdout.strip() == '{}'

    # manipulation
    config_path = generate_random_string()
    s = generate_random_string()
    config = {}
    config_manipulated = {
        'logging': {'root': {'level': 'DEBUG', 'handlers': "richconsole"}},
        'path': {'to': {'key': s}},
    }
    with patch('ubw.load_config') as p_load:
        p_load.return_value = config
        with patch('ubw.init_logging') as p_log:
            with patch('ubw.init_sentry') as p_sentry:
                with patch('pdb_attach.listen') as p_listen:
                    result = runner.invoke(
                        ubw.app,
                        ['--config', config_path,
                         '--verbose',
                         '--config-override', f'path.to.key="{s}"',
                         '--remote-debug-with-port', '10203',
                         'print-config'])
                    p_load.assert_called_once_with(Path(config_path))
                    p_log.assert_called_once_with(config_manipulated)
                    p_sentry.assert_called_once_with(config_manipulated)
                    p_listen.assert_called_once_with(10203)
    assert result.exit_code == 0
