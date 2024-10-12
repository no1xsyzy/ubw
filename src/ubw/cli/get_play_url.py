import os
import re
import shutil
import sys
from contextlib import asynccontextmanager
from enum import Enum

from ubw.utils import sync


class _OutputChoice(str, Enum):
    url_only = 'url_only'
    info_link = 'info_link'
    info_link_url = 'info_link_url'
    tsv = 'tsv'
    m3u = 'm3u'
    raw = 'raw'
    raw_pretty = 'raw_pretty'
    analyzer = 'analyzer'
    libmpv = 'libmpv'
    m3u_mpv = 'm3u_mpv'


@asynccontextmanager
async def raw(play_info):
    print(play_info.model_dump_json())
    yield None


@asynccontextmanager
async def raw_pretty(play_info):
    from rich.pretty import pprint
    pprint(play_info)
    yield None


@asynccontextmanager
async def info_link(play_info):
    from rich import get_console
    console = get_console()
    from rich.text import Text

    def each(url, info):
        console.print(Text(info), style=f"link {url}")

    yield each


@asynccontextmanager
async def info_link_url(play_info):
    from rich import get_console
    console = get_console()
    from rich.text import Text

    def each(url, info):
        console.print(Text(f"{info}\t{url}"), style=f"link {url}")

    yield each


@asynccontextmanager
async def url_only(play_info):
    def each(url, info):
        print(url)

    yield each


@asynccontextmanager
async def tsv(play_info):
    def each(url, info):
        print('\t'.join([info, *info[1:-1].split("|"), "", url]))

    yield each


@asynccontextmanager
async def m3u(play_info):
    from itertools import count
    print("#EXTM3U")
    s = count()

    def each(url, info):
        print(f"#EXTINF:,[{next(s)}]{info}\n{url}\n")

    yield each


@asynccontextmanager
async def m3u_mpv(play_info):
    from itertools import count
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.m3u', mode='wt', encoding='utf-8') as m3u8file:
        print("#EXTM3U", file=m3u8file)
        s = count()

        def each(url, info):
            print(f"#EXTINF:,[{next(s)}]{info}\n{url}\n", file=m3u8file)

        yield each

        m3u8file.flush()

        returncode = os.spawnl(os.P_WAIT, shutil.which('mpv'),
                               'mpv', m3u8file.name)
        print('mpv process exited with code {}'.format(returncode))


@asynccontextmanager
async def libmpv(play_info):
    os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]
    import mpv

    from ubw.cli import main
    mpv_configs = main.config.get('mpv_configs', {})

    player = mpv.MPV(
        ytdl=True,
        input_default_bindings=True, input_vo_keyboard=True, osc=True, osd_font_size=35,
        **mpv_configs,
    )

    def each(url, info):
        print(info, url)
        player.loadfile(url, 'append-play', title=info, force_media_title=info)

    yield each

    player.wait_for_shutdown()


@asynccontextmanager
async def analyzer(play_info):
    from urllib.parse import urlparse
    columns = set()
    records = []

    def each(url, info):
        scheme, netloc, path, _, query, _ = urlparse(url)
        r = {'Name': info, 'Host': netloc, 'Url': url}
        for p in query.split('&'):
            a, b = p.split('=')
            if a not in columns:
                columns.add(a)
            r[a] = b
        records.append(r)

    yield each

    import csv
    writer = csv.DictWriter(sys.stdout, fieldnames=('Name', 'Host', 'Url', *sorted(columns)))
    writer.writeheader()
    writer.writerows(records)


_OUTPUT_MAP = {
    _OutputChoice.url_only: url_only,
    _OutputChoice.info_link: info_link,
    _OutputChoice.info_link_url: info_link_url,
    _OutputChoice.tsv: tsv,
    _OutputChoice.m3u: m3u,
    _OutputChoice.raw: raw,
    _OutputChoice.raw_pretty: raw_pretty,
    _OutputChoice.analyzer: analyzer,
    _OutputChoice.libmpv: libmpv,
    _OutputChoice.m3u_mpv: m3u_mpv,
}


def extend_urlinfo(stream, fmt, cdc, url_info, real_original):
    host = url_info.host.replace('https://', '')
    url = f"{url_info.host}{cdc.base_url}{url_info.extra}"
    compressed = re.search(r"(\d+)_(?:minihevc|prohevc|bluray)", url)
    if compressed:
        info = f"C|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}"
    else:
        info = f"A|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}"
    yield url, info
    if real_original:
        if stream.protocol_name == 'http_stream':
            return  # seems unsupported
        if compressed:
            yield (re.sub(r"(\d+)_(?:minihevc|prohevc|bluray)", r'\1', url),
                   f"T|{stream.protocol_name}|{fmt.format_name}|{cdc.codec_name}|{cdc.current_qn}|{host}")


@sync
async def get_play_url(room_id: int,
                       output: _OutputChoice = _OutputChoice.info_link,
                       qn: int = 10000,
                       filter_protocol: str = '',
                       filter_format: str = '',
                       filter_codec: str = '',
                       print_first: bool = False,
                       real_original: bool = True,
                       ):
    from ubw.clients import BilibiliCookieClient

    from ubw.cli import main
    async with BilibiliCookieClient(**main.config['accounts']['default']) as client:
        play_info = await client.get_room_play_info(room_id, qn)

    out_mgr = _OUTPUT_MAP.get(output)

    async with out_mgr(play_info) as each:
        if not callable(each):
            return
        if play_info.playurl_info is None:
            return
        if play_info.playurl_info.playurl is None:
            return
        for stream in play_info.playurl_info.playurl.stream:
            if filter_protocol != '' and stream.protocol_name not in filter_protocol:
                continue
            for fmt in stream.format:
                if filter_format != '' and fmt.format_name not in filter_format:
                    continue
                for cdc in fmt.codec:
                    if qn != cdc.current_qn:
                        continue
                    if filter_codec != '' and cdc.codec_name not in filter_codec:
                        continue
                    for url_info in cdc.url_info:
                        for u, i in extend_urlinfo(stream, fmt, cdc, url_info, real_original):
                            each(u, i)
                            if print_first:  # should remove?
                                return
