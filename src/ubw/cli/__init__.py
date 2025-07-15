import asyncio
from pathlib import Path
from typing import Annotated

import typer

from ubw.app import AppTypeAdapter
from ubw.cli.get_play_url import get_play_url
from ubw.utils import sync, listen_to_all

app = typer.Typer()


def init_sentry(cd):
    import sentry_sdk
    sentry_sdk.init(**cd['sentry'])


def init_logging(cd):
    import logging.config
    logging.config.dictConfig(cd['logging'])


def load_config(c: Path):
    import toml
    with c.open(encoding='utf-8') as f:
        return toml.load(f)


NOT_MODIFY = object()


def patch_config(config: dict, patch: dict, *, toml_patch: list[str] | tuple[str, ...] = None):
    new_config = {}
    if patch is not None:
        assert isinstance(patch, dict)
        for k in config.keys() | patch.keys():
            vp = patch.get(k, NOT_MODIFY)
            if vp is NOT_MODIFY:
                if k in config:
                    new_config[k] = config[k]
            elif isinstance(vp, dict) and isinstance(config.get(k, None), dict):
                new_config[k] = patch_config(config[k], vp)
            else:
                new_config[k] = vp
    if toml_patch is not None:
        if isinstance(toml_patch, (list, tuple)):
            toml_patch = '\n'.join(toml_patch)
        import toml
        return patch_config(config, toml.loads(toml_patch))
    return new_config


@app.command('ss')
@app.command('strange_stalker')
@sync
async def strange_stalker(
        rooms: Annotated[list[int], typer.Argument(help="")],
        regex: Annotated[list[str], typer.Option("--regex", "-r")] = None,
        uids: Annotated[list[int], typer.Option("--uids", "-u")] = None,
        ignore_danmaku: Annotated[list[int], typer.Option("--ignore", "-i")] = None,
        derive_uids: bool = True,
        derive_regex: bool = True,
):
    from ubw.handlers import StrangeStalkerHandler
    if regex is None:
        regex = []
    if uids is None:
        uids = []
    if ignore_danmaku is None:
        ignore_danmaku = []
    if derive_uids:
        from ubw.clients import BilibiliUnauthorizedClient
        async with BilibiliUnauthorizedClient() as client:
            uids.extend([i.room_info.uid
                         for i in await asyncio.gather(*(client.get_info_by_room(room)
                                                         for room in rooms))])
    if derive_regex:
        regex.extend(map(str, uids))
        regex.extend(map(str, rooms))
    regex = '|'.join(regex)
    ignore_danmaku = '|'.join(ignore_danmaku)
    return await listen_to_all(rooms, StrangeStalkerHandler(uids=uids, regex=regex, ignore_danmaku=ignore_danmaku))


@app.command('p')
@app.command('danmakup')
@sync
async def danmakup(
        rooms: list[int],
        ignore_danmaku: Annotated[list[str], typer.Option("--ignore", "-i")] = None,
        ignore_rate: float = 0.,
        dim_rate: float = .25,
        show_interact_word: bool = False,
        test_flags: str = "",
):
    from ubw.handlers import DanmakuPHandler
    if ignore_danmaku:
        ignore_danmaku = '|'.join(ignore_danmaku)
    else:
        ignore_danmaku = None

    settings = {
        'ignore_danmaku': ignore_danmaku,
        'ignore_rate': ignore_rate,
        'dim_rate': dim_rate,
        'show_interact_word': show_interact_word,
        'test_flags': test_flags,
    }

    ui = None

    for s in test_flags.split(','):
        if s.startswith('use_ui='):
            ui = s[len('use_ui='):]

    if ui is None:
        handler = DanmakuPHandler(**settings)
        await listen_to_all(rooms, handler)
    elif ui == 'live':
        from ubw.ui.stream_view import LiveStreamView
        ui = LiveStreamView(alternate_screen=True)
        handler = DanmakuPHandler(**settings, ui=ui, owned_ui=False)
        async with ui:
            await listen_to_all(rooms, handler)
    elif ui == 'rich':
        from ubw.ui.stream_view import Richy
        ui = Richy()
        handler = DanmakuPHandler(**settings, ui=ui, owned_ui=False)
        async with ui:
            await listen_to_all(rooms, handler)
    elif ui == 'web':
        from ubw.ui.stream_view import Web
        ui = Web()
        handler = DanmakuPHandler(**settings, ui=ui, owned_ui=False)
        async with ui:
            await listen_to_all(rooms, handler)
    else:
        raise NotImplementedError(f'{ui=} not supported yet')


@app.command('pian')
@sync
async def pian(rooms: list[int]):
    from ubw.handlers import PianHandler
    await listen_to_all(rooms, PianHandler())


@app.command('bhashm')
@sync
async def bhashm(rooms: list[int], famous_people: Annotated[list[int], typer.Option("--famous", "-f")] = None):
    from ubw.handlers import HashMarkHandler
    await listen_to_all(rooms, HashMarkHandler(famous_people=famous_people))


@app.command('dump_raw')
@sync
async def dump_raw(rooms: list[int]):
    from ubw.handlers import DumpRawHandler
    await listen_to_all(rooms, handler_factory=lambda r: DumpRawHandler(room_id=r))


@app.command('saver')
@app.command('s')
@sync
async def saver(rooms: list[int]):
    from ubw.handlers import SaverHandler
    await listen_to_all(rooms, handler_factory=lambda r: SaverHandler(room_id=r))


@app.command('test_account')
@app.command('t')
@sync
async def test_account(account_file: Path = 'cookies.txt'):
    from rich import print
    from ubw.clients.bilibili import BilibiliCookieClient
    async with BilibiliCookieClient(cookie_file=account_file) as c:
        print(await c.get_nav())


@app.command('living_status')
@app.command('w')
@sync
async def living_status(
        rooms: Annotated[list[int], typer.Option("--rooms", "-r")] = (),
        from_user: Annotated[list[int], typer.Option("--from-user", "-u")] = (),
        from_dynamic: Annotated[list[int], typer.Option("--from-dynamic", "-d")] = (),
):
    from pydantic import TypeAdapter
    from ubw.clients.bilibili import BilibiliClient
    from ubw.handlers import LivingStatusHandler
    from ubw import models

    from_user = set(from_user)
    from_dynamic = set(from_dynamic)
    rooms = set(rooms)

    async with TypeAdapter(BilibiliClient).validate_python(main.config['accounts']['default']) as c:
        c: BilibiliClient
        for d in from_dynamic:
            f: models.Dynamic = await c.get_dynamic(d, features=('itemOpusStyle',))
            for t in f.item.rich_text_nodes:
                if isinstance(t, models.bilibili.RichTextNodeTypeAt):
                    from_user.add(t.rid)

        for m in from_user:
            acc = await c.get_account_info(m)
            rooms.add(acc.live_room_id)

        await listen_to_all(list(rooms),
                            LivingStatusHandler(bilibili_client=c, bilibili_client_owner=False),
                            b_client=c)


@app.command('run')
@app.command('r')
@sync
async def run(cc: list[str]):
    coroutines = []
    for c in cc:
        match c.split('.'):
            case ['strange_stalker' | 'ss', k]:
                coroutines.append(strange_stalker.__wrapped__(**main.config['strange_stalker'][k]))
            case ['danmakup' | 'p', k]:
                coroutines.append(danmakup.__wrapped__(**main.config['danmakup'][k]))
            case ['pian', k]:
                coroutines.append(pian.__wrapped__(**main.config['pian'][k]))
            case ['bhashm' | 'h', k]:
                coroutines.append(bhashm.__wrapped__(**main.config['bhashm'][k]))
            case ['dump_raw' | 'd', k]:
                coroutines.append(dump_raw.__wrapped__(**main.config['dump_raw'][k]))
            case ['saver' | 's', k]:
                coroutines.append(saver.__wrapped__(**main.config['saver'][k]))
            case _:
                print(f"unknown mod {c}, skipped")
    await asyncio.gather(*coroutines)


@app.command('app_show')
@sync
async def app_show(
        app_name: str,
        app_override: Annotated[list[str], typer.Option('--app-override', '-X')] = (),
        raw: bool = False,
):
    appconf = main.config['apps'].get(app_name)
    appconf = patch_config(appconf, {}, toml_patch=app_override)
    from rich.pretty import pprint
    if raw:
        pprint(appconf)
        return appconf
    application = AppTypeAdapter.validate_python(appconf)
    pprint(application)
    return application


@app.command('app_run')
@sync
async def app_run(
        app_name: str,
        app_override: Annotated[list[str], typer.Option('--app-override', '-X')] = (),
):
    appconf = main.config['apps'].get(app_name)
    appconf = patch_config(appconf, {}, toml_patch=app_override)
    application = AppTypeAdapter.validate_python(appconf)
    try:
        await application.start()
        await application.join()
    finally:
        await application.stop()
        await application.close()


app.command()(get_play_url)


@app.command()
@sync
async def shark(
        expr: str,
        rooms: list[int],
        directory: Annotated[Path, typer.Option('--dir', '-d')] = 'output/shark'
):
    from ubw.handlers.shark import SharkHandler
    handler = SharkHandler(rule=expr, out_dir=directory)
    await listen_to_all(rooms, handler)


@app.command()
def print_config():
    from rich import print
    print(main.config)


@app.command()
def print_dirs():
    from ubw.userdata import user_data_path, user_config_path
    print(f"{user_data_path   = }")
    print(f"{user_config_path = }")


@app.callback()
def main(
        cd: Annotated[Path, typer.Option('--config', '-c')] = "config.toml",
        sentry: Annotated[bool, typer.Option(' /--no-sentry', ' /-S')] = True,
        log: bool = True,
        verbose: Annotated[int, typer.Option('--verbose', '-v', count=True)] = 0,
        remote_debug_with_port: int = 0,
        config_override: Annotated[list[str], typer.Option('--config-override', '-D')] = (),
):
    cd = Path(cd)
    config = load_config(cd)
    if log:
        if verbose > 1:
            config_override.append('logging.root.level="DEBUG"')
        if verbose > 0:
            config_override.append('logging.root.handlers=["rich"]')
    config = patch_config(config, {}, toml_patch=config_override)
    main.config = config
    if log:
        init_logging(config)
    if sentry:
        init_sentry(config)
    if 0 < remote_debug_with_port < 65536:
        import pdb_attach
        pdb_attach.listen(remote_debug_with_port)
