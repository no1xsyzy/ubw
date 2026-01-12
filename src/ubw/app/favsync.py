import asyncio
import json
import logging
import os
import warnings
from contextlib import nullcontext, asynccontextmanager
from pathlib import Path

import aiofiles
import aiofiles.os
from bilibili_api import video, HEADERS, get_client
from bilibili_api.favorite_list import FavoriteList
from pydantic import TypeAdapter, field_validator

from ._base import *
from ..clients import BilibiliClient
from ..models import FavList, Response

logger = logging.getLogger('favsync')


class FavSyncApp(BaseApp):
    cls: Literal['favsync'] = 'favsync'

    favlist_id: int
    target_path: Path

    # low config
    ffmpeg: Path = None

    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True

    @field_validator('target_path', mode='after')
    @classmethod
    def absolute_target_path(cls, v: Path):
        return v.resolve()

    @field_validator('ffmpeg', mode='before')
    @classmethod
    def find_ffmpeg(cls, v):
        if v is not None:
            return v
        gen_possible_names = (
            Path(i) / fn
            for i in os.environ['PATH'].split(os.path.pathsep)
            for fn in ['ffmpeg', 'ffmpeg.exe']
        )
        for p in gen_possible_names:
            if p.is_file():
                return p
        return None

    async def _fetch_fav_list(self, credential):
        fav_list = FavoriteList(media_id=self.favlist_id, credential=credential)
        has_more = True
        page = 1
        while has_more:
            content = TypeAdapter(Response[FavList]).validate_python(await fav_list.get_content(page=page))
            for media in content.data.medias:
                yield media
            has_more = content.data.has_more
            page += 1

    @asynccontextmanager
    async def _archive(self):
        archive = {}
        if (self.target_path / '.archive.json').exists():
            async with aiofiles.open(self.target_path / '.archive.json') as f:
                archive = json.loads(await f.read())
                if not isinstance(archive, dict):
                    warnings.warn('Archive is not a dict')
                    archive = {}

        yield archive

        async with aiofiles.open(self.target_path / 'archive.json.tmp', 'w') as f:
            await f.write(json.dumps(archive, ensure_ascii=False, indent=2))

        await aiofiles.os.replace(self.target_path / 'archive.json.tmp', self.target_path / 'archive.json')

    async def _run(self):
        if not self.target_path.is_dir():
            raise FileNotFoundError(f'{self.target_path} is not a directory')
        archive = {}
        if (self.target_path / '.archive.json').exists():
            async with aiofiles.open(self.target_path / '.archive.json') as f:
                archive = json.loads(await f.read())
                if not isinstance(archive, dict):
                    warnings.warn('Archive is not a dict')
                    archive = {}
        async with (self.bilibili_client if self.bilibili_client_owner else nullcontext()):
            credential = await self.bilibili_client.make_credential()
            async for media in self._fetch_fav_list(credential):
                bvid = media.bvid
                bvid_root = self.target_path / f'{media.title} [{bvid}]'
                for page in range(1, media.page + 1):
                    status = set(archive.get(bvid, []))
                    if 'v1' not in status:
                        v = video.Video(bvid=bvid, credential=credential)
                        download_url_data = await v.get_download_url()
                        detector = video.VideoDownloadURLDataDetecter(data=download_url_data)
                        streams = detector.detect_best_streams()
                        if detector.check_flv_mp4_stream():
                            # FLV
                            final_path = bvid_root / f'p{page}.flv'
                            await self._download_file(streams[0].url, final_path, f"{bvid} FLV流")
                            print(f'已下载到 {final_path}')
                        else:
                            # MP4
                            tmp_video = bvid_root / f'p{page}_video_temp.m4s'
                            tmp_audio = bvid_root / f'p{page}_audio_temp.m4s'
                            final_path = bvid_root / f'p{page}.mp4'
                            await self._download_file(streams[0].url, tmp_video, f"{bvid} 视频流")
                            await self._download_file(streams[1].url, tmp_audio, f"{bvid} 音频流")
                            proc = await asyncio.create_subprocess_exec(
                                str(self.ffmpeg), '-i', str(tmp_video), '-i', str(tmp_audio),
                                '-c:v', 'copy', '-c:a', 'copy', str(final_path),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                            )
                            stdout, stderr = await proc.communicate()
                            if proc.returncode != 0:
                                stdout = stdout.decode(errors='ignore')
                                stderr = stderr.decode(errors='ignore')
                                logger.error(
                                    f'{bvid} ffmpeg 混流失败，保留临时文件：' '\n'
                                    f'视频：{tmp_video}' '\n'
                                    f'音频：{tmp_audio}' '\n'
                                    '\n'
                                    '==STDOUT==\n'
                                    f'{stdout}' '\n'
                                    '\n'
                                    '==STDERR==\n'
                                    f'{stderr}')
                            else:
                                await aiofiles.os.remove(tmp_video)
                                await aiofiles.os.remove(tmp_audio)
                                print(f'已下载到 {final_path}')

        async with aiofiles.open(self.target_path / 'archive.json.tmp', 'w') as f:
            await f.write(json.dumps(archive, ensure_ascii=False, indent=2))

        await aiofiles.os.replace(self.target_path / 'archive.json.tmp', self.target_path / 'archive.json')

        self._task = None

    async def _download_file(self, url: str, out: Path, intro: str) -> list[Path]:
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            dwn_id = await get_client().download_create(url, HEADERS)
            bts = 0
            tot = get_client().download_content_length(dwn_id)
            async with aiofiles.open(self.out_dir / out, mode='wb') as f:
                while True:
                    bts += await f.write(await get_client().download_chunk(dwn_id))
                    print(f"{intro} - {out} [{bts} / {tot}]", end="\r")
                    if bts == tot:
                        break
            return [out]
        except Exception as e:
            logger.exception('exception in download_file()', exc_info=e)
            return []
        except BaseException as e:
            logger.exception('exception in download_file()', exc_info=e)
            raise

    async def close(self):
        pass
