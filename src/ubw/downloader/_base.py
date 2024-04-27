import asyncio
import logging
from functools import cached_property
from os import PathLike
from pathlib import Path
from typing import Coroutine, Any, TypeAlias

import aiofiles
import aiohttp
from pydantic import BaseModel

PathList: TypeAlias = list[str | PathLike[str]]
logger = logging.getLogger('downloader')


class BaseDownloader(BaseModel):
    # low config
    out_dir: Path = Path('output/download')
    chunk_size: int = 1 * 1024 * 1024  # 1M

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    # runtime
    @cached_property
    def _session(self):
        return aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(sock_connect=10))

    async def download_file(self, url, target, *, get_kwargs=None, session=None) -> PathList:
        try:
            return await self._download_file(url, target, get_kwargs=get_kwargs, session=session)
        except Exception as e:
            logger.exception('exception in download_file()', exc_info=e)
        except BaseException as e:
            logger.exception('exception in download_file()', exc_info=e)
            raise

    async def _download_file(self, url, target, *, get_kwargs=None, session=None) -> PathList:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        async with (session or self._session).get(url, **(get_kwargs or {})) as resp:
            async with aiofiles.open(self.out_dir / target, mode='wb') as f:
                content_length = resp.content_length
                received = 0
                async for chunk in resp.content.iter_chunked(self.chunk_size):
                    chunk: bytes
                    received += len(chunk)
                    print(f'{target} completed {received}/{content_length}')
                    await f.write(chunk)
        return [target]

    async def gather_download(self, downloads: list[Coroutine[Any, Any, PathList]]) -> PathList:
        gathered: tuple[PathList, ...] = await asyncio.gather(*downloads)
        return [x for xx in gathered for x in xx]

    async def close(self):
        if '_session' in self.__dict__:
            await self._session.close()
