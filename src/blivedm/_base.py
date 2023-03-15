from __future__ import annotations

import abc
from typing import Protocol

__all__ = ('HandlerInterface', 'ClientABC')


class HandlerInterface(Protocol):
    """直播消息处理器接口"""

    async def handle(self, client: ClientABC, command: dict):
        raise NotImplementedError


class ClientABC(abc.ABC):
    room_id: int

    def __init__(self):
        self._handlers: list[HandlerInterface] = []
        self._task = None

    def add_handler(self, handler: HandlerInterface):
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler: HandlerInterface):
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    @property
    def is_running(self):
        return self._task is not None

    @abc.abstractmethod
    def start(self):
        ...

    @abc.abstractmethod
    async def join(self):
        ...

    @abc.abstractmethod
    def stop(self):
        ...

    @abc.abstractmethod
    async def close(self):
        ...

    async def stop_and_close(self):
        task = self._task
        if task:
            self.stop()
            await task
        await self.close()
