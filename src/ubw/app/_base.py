import abc
import asyncio
import logging
import warnings
from typing import Literal

from pydantic import BaseModel

__all__ = (
    'BaseApp', 'InitLoopFinalizeApp',
    'Literal',
)

logger = logging.getLogger('app._base')


class BaseApp(BaseModel, abc.ABC):
    cls: str
    _task: asyncio.Task | None = None

    def start(self):
        if self._task is not None:
            return warnings.warn("This app is already running")
        self._task = asyncio.create_task(self._run())

    @abc.abstractmethod
    async def _run(self):
        ...

    async def join(self):
        if self._task is None:
            return warnings.warn('This app is stopped, cannot join()')
        logger.debug('app=%s joining', self)
        await asyncio.shield(self._task)

    def stop(self):
        task = self._task
        if task is None:
            return warnings.warn('This app is stopped, cannot stop() again')
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


class InitLoopFinalizeApp(BaseApp, abc.ABC):
    @abc.abstractmethod
    async def _init(self):
        pass

    @abc.abstractmethod
    async def _loop(self):
        pass

    @abc.abstractmethod
    async def _finalize(self):
        pass

    async def _run(self):
        try:
            await self._init()
            while True:
                await self._loop()
        finally:
            await self._finalize()
