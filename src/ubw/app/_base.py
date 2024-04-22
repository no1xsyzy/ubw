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

    async def start(self):
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
        await self._task

    async def stop(self):
        task = self._task
        self._task = None
        if task is None:
            return warnings.warn('This app is stopped, cannot stop() again')
        if task.cancel('stop'):
            try:
                await task
            except asyncio.CancelledError:
                return

    @abc.abstractmethod
    async def close(self):
        ...

    async def stop_and_close(self):
        try:
            await self.stop()
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
