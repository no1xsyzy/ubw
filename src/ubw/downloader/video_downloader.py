import os
from operator import attrgetter

from pydantic import field_validator

from ubw.clients import BilibiliClient
from ._base import *


class VideoDownloader(BaseDownloader):
    # low config
    ffmpeg: Path = None

    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True

    async def __aenter__(self):
        if self.bilibili_client_owner:
            await self.bilibili_client.__aenter__()
        return await super().__aenter__()

    @field_validator('ffmpeg', mode='before')
    @classmethod
    def find_ffmpeg(cls, v):
        if v is not None:
            return v
        c = (Path(i) / fn
             for i in os.environ['PATH'].split(os.path.pathsep)
             for fn in ['ffmpeg', 'ffmpeg.exe'])
        for p in c:
            if p.is_file():
                return p
        return None

    async def download_bvid(self, bvid) -> PathList:
        pages = await self.bilibili_client.get_video_pagelist(bvid)
        return [y
                for x in await asyncio.gather(*[self.download_cid(bvid, page.cid, f"{bvid}_p{idx}")
                                                for idx, page in enumerate(pages)])
                for y in x]

    async def download_cid(self, bvid, cid, target=None) -> PathList:
        if target is None:
            target = f"{bvid}_c{cid}"
        vd = await self.bilibili_client.get_video_download(bvid, cid)
        for video in vd.dash.video:
            print(f'{video.id=} {video.bandwidth=}')
        for audio in vd.dash.audio:
            print(f'{audio.id=} {audio.bandwidth=}')
        chosen_video = max(vd.dash.video, key=attrgetter('id', 'bandwidth'))
        chosen_audio = max(vd.dash.audio, key=attrgetter('bandwidth'))
        print(f'{chosen_video.id=} {chosen_video.apparent_fid=} {chosen_video.bandwidth=}')
        print(f'{chosen_audio.id=} {chosen_audio.apparent_fid=} {chosen_audio.bandwidth=}')
        get_kwargs = {'headers': {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            'referer': 'https://www.bilibili.com/video/' + bvid}}
        await asyncio.gather(self.download_file(chosen_video.base_url, target + f".f{chosen_video.apparent_fid}.m4s",
                                                get_kwargs=get_kwargs),
                             self.download_file(chosen_audio.base_url, target + f".f{chosen_audio.apparent_fid}.m4a",
                                                get_kwargs=get_kwargs))
        # todo: ffmpeg re-mux
        return [Path(f'{target}.mp4')]

    async def close(self):
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
        await super().close()
