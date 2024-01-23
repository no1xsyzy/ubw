from __future__ import annotations

import abc
import enum
import logging
import struct
from asyncio import Task
from functools import cached_property
from typing import Protocol, NamedTuple

from pydantic import BaseModel

__all__ = (
    # types
    'HandlerInterface',
    'ClientABC',
    'HeaderTuple',

    # exceptions
    'InitError',
    'AuthError',

    # enums
    'ProtoVer',
    'Operation',
    'AuthReplyCode',

    # consts
    'DEFAULT_DANMAKU_SERVER_LIST',
    'HEADER_STRUCT',
)

logger = logging.getLogger('ubw.clients')


class HandlerInterface(Protocol):
    """直播消息处理器接口"""

    async def handle(self, client: ClientABC, command: dict):
        raise NotImplementedError


class ClientABC(BaseModel, abc.ABC):
    clientc: str
    room_id: int

    @cached_property
    def _handlers(self) -> list[HandlerInterface]:
        return []

    @cached_property
    def _task(self) -> Task | None:
        return None

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


class InitError(Exception):
    """初始化失败"""


class AuthError(Exception):
    """认证失败"""


class HeaderTuple(NamedTuple):
    pack_len: int
    raw_header_size: int
    ver: int
    operation: int
    seq_id: int


# WS_BODY_PROTOCOL_VERSION
class ProtoVer(enum.IntEnum):
    NORMAL = 0
    HEARTBEAT = 1
    DEFLATE = 2
    BROTLI = 3


# go-common\app\service\main\broadcast\model\operation.go
class Operation(enum.IntEnum):
    HANDSHAKE = 0
    HANDSHAKE_REPLY = 1
    HEARTBEAT = 2
    HEARTBEAT_REPLY = 3
    SEND_MSG = 4
    SEND_MSG_REPLY = 5
    DISCONNECT_REPLY = 6
    AUTH = 7
    AUTH_REPLY = 8
    RAW = 9
    PROTO_READY = 10
    PROTO_FINISH = 11
    CHANGE_ROOM = 12
    CHANGE_ROOM_REPLY = 13
    REGISTER = 14
    REGISTER_REPLY = 15
    UNREGISTER = 16
    UNREGISTER_REPLY = 17
    # B站业务自定义OP
    # MinBusinessOp = 1000
    # MaxBusinessOp = 10000


# WS_AUTH
class AuthReplyCode(enum.IntEnum):
    OK = 0
    TOKEN_ERROR = -101


DEFAULT_DANMAKU_SERVER_LIST = [
    {'host': 'broadcastlv.chat.bilibili.com', 'port': 2243, 'wss_port': 443, 'ws_port': 2244}
]
HEADER_STRUCT = struct.Struct('>I2H2I')
