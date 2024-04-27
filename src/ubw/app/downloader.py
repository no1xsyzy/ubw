from typing import Union

from pydantic import model_validator

from ._base import *
from ..clients import BilibiliClient
from ..downloader.dynamic_downloader import DynamicDownloader
from ..downloader.video_downloader import VideoDownloader

Query = Union[
    tuple[Literal['dynamic'], int | str],
    tuple[Literal['bvid'], str],
    tuple[Literal['cid'], str, int | str],
]


class DownloaderApp(BaseApp):
    cls: Literal['downloader'] = 'downloader'

    queries: list[Query] = []

    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True
    video_downloader: VideoDownloader | None = None
    video_downloader_owner: bool = True
    dynamic_downloader: DynamicDownloader | None = None
    dynamic_downloader_owner: bool = True

    @model_validator(mode='after')
    def di(self):
        if self.video_downloader is None:
            self.video_downloader = VideoDownloader(
                bilibili_client=self.bilibili_client, bilibili_client_owner=False,
            )
        if self.dynamic_downloader is None:
            self.dynamic_downloader = DynamicDownloader(
                bilibili_client=self.bilibili_client, bilibili_client_owner=False,
                video_downloader=self.video_downloader, video_downloader_owner=False,
            )
        return self

    async def _run(self):
        if self.dynamic_downloader_owner:
            await self.dynamic_downloader.__aenter__()
        if self.video_downloader_owner:
            await self.video_downloader.__aenter__()
        if self.bilibili_client_owner:
            await self.bilibili_client.__aenter__()

        for query in self.queries:
            await self.run_query(query)

    async def run_query(self, query: Query):
        match query:
            case ['dynamic', dyn_id]:
                await self.dynamic_downloader.download_dynamic(str(dyn_id))
            case ['bvid', bvid]:
                await self.video_downloader.download_bvid(bvid)
            case ['cid', bvid, cid]:
                await self.video_downloader.download_cid(bvid, cid)

    async def close(self):
        if self.dynamic_downloader_owner:
            await self.dynamic_downloader.close()
        if self.video_downloader_owner:
            await self.video_downloader.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
