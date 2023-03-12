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

    @abc.abstractmethod
    def __init__(self): ...

    @abc.abstractmethod
    def add_handler(self, handler: HandlerInterface): ...

    @abc.abstractmethod
    def start(self): ...

    @abc.abstractmethod
    async def join(self): ...

    @abc.abstractmethod
    def stop(self): ...

    @abc.abstractmethod
    async def close(self): ...

    @abc.abstractmethod
    async def stop_and_close(self): ...
