import abc
import asyncio
import logging
import warnings
from typing import Literal

from pydantic import BaseModel

__all__ = ('BaseApp', 'Literal',)

logger = logging.getLogger('app._base')


class BaseApp(BaseModel, abc.ABC):
    cls: str
    _task: asyncio.Task | None = None

    def start(self):
        if self._task is not None:
            warnings.warn("This app is already running")
            return
        self._task = asyncio.create_task(self._run())

    @abc.abstractmethod
    async def _run(self):
        ...

    async def join(self):
        if self._task is None:
            warnings.warn('This app is stopped, cannot join()')
            return

        logger.debug('app=%s joining', self)
        await asyncio.shield(self._task)

    def stop(self):
        if not self.is_running:
            warnings.warn('This app is stopped, cannot stop() again')
            return

        task = self._task
        if task is None:
            return
        if task.cancel('stop'):
            self._task = None
            return task

    @abc.abstractmethod
    async def close(self):
        ...

    async def stop_and_close(self):
        try:
            task = self.stop()
            if task is not None:
                await task
        finally:
            await self.close()
