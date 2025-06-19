from aiofiles.threadpool.text import AsyncTextIOWrapper
from pydantic import model_validator

from ubw.clients import BilibiliClient
from ._base import *
from .video_downloader import VideoDownloader
from .. import models


class DynamicDownloader(BaseDownloader):
    # DI
    bilibili_client: BilibiliClient
    bilibili_client_owner: bool = True
    video_downloader: VideoDownloader | None = None
    video_downloader_owner: bool = True

    async def __aenter__(self):
        if self.video_downloader_owner:
            await self.video_downloader.__aenter__()
        if self.bilibili_client_owner:
            await self.bilibili_client.__aenter__()
        return await super().__aenter__()

    @model_validator(mode='after')
    def di(self):
        if self.video_downloader is None:
            self.video_downloader = VideoDownloader(
                bilibili_client=self.bilibili_client, bilibili_client_owner=False,
            )

    async def download_dynamic(self, dyn_id) -> PathList:
        return await self.download_dynamic_item((await self.bilibili_client.get_dynamic(dyn_id)).item)

    async def download_dynamic_item(self, dynamic_item: models.DynamicItem) -> PathList:
        dt_str = dynamic_item.pub_date.strftime("%Y年%m月%d日%H时%M分%S秒")
        name = dynamic_item.modules.module_author.name
        fname = f"{dt_str} {name}.md"
        md_path = self.out_dir / fname
        async with aiofiles.open(md_path, mode='wt', encoding='utf-8') as f:
            f: AsyncTextIOWrapper
            await f.write(dynamic_item.markdown)
            await f.write("\n\n")
            for asset in await self.download_assets(dynamic_item):
                await f.write(f"![]({asset})")
        return [fname]

    async def download_dynamic_pics(self, dynamic_item: models.DynamicItem) -> PathList:
        return [y
                for x in await asyncio.gather(*(self.download_file(pic, f'{dynamic_item.id_str}-{idx}.png')
                                                for idx, pic in enumerate(dynamic_item.pictures)))
                for y in x]

    async def download_dynamic_video(self, dynamic_item: models.DynamicItem) -> PathList:
        if not dynamic_item.is_video:
            return []
        return await self.video_downloader.download_bvid(dynamic_item.modules.module_dynamic.major.root.archive.bvid)

    async def download_assets(self, dynamic_item: models.DynamicItem):
        pics, videos = await asyncio.gather(self.download_dynamic_pics(dynamic_item),
                                            self.download_dynamic_video(dynamic_item))
        return pics + videos

    async def close(self):
        if self.video_downloader_owner:
            await self.video_downloader.close()
        if self.bilibili_client_owner:
            await self.bilibili_client.close()
        await super().close()
