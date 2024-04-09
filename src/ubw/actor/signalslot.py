from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

_T = TypeVar('_T')


class Slot(Generic[_T]):
    def __init__(self, queue: asyncio.Queue[_T]):
        self._queue = queue

    async def put(self, v: _T):
        await self._queue.put(v)

    def put_nowait(self, v: _T):
        self._queue.put_nowait(v)


class Signal(Generic[_T]):
    def __init__(self, queue: asyncio.Queue[_T]):
        self._queue = queue
        self.connect_task: asyncio.Task | None = None

    async def get(self) -> _T:
        return await self._queue.get()

    def get_nowait(self) -> _T:
        return self._queue.get_nowait()

    def connect(self, slot: Slot[_T]):
        if self.connect_task is not None:
            raise ValueError('signal is connected')
        self.connect_task = ct = asyncio.create_task(self._c(slot))
        return ct

    async def _c(self, slot: Slot[_T]):
        while True:
            v = await self.get()
            await slot.put(v)


class SlotProperty(Generic[_T]):
    def __init__(self, name):
        self.ssname = name
        self.attrname = None

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same slot to two different names "
                f"({self.attrname!r} and {name!r})."
            )
        elif name not in [self.ssname, '_' + self.ssname]:
            raise TypeError(
                "Cannot assign slot name different from signalslot name "
                f"({self.ssname!r} != {name})")

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use slot instance without calling __set_name__ on it.")
        cache = instance.__dict__
        slot = cache.get(self.attrname)
        if slot is None:
            queue = getattr(instance, '_queue_' + self.ssname, None)
            if queue is None:
                queue = asyncio.Queue()
                setattr(instance, '_queue_' + self.ssname, queue)
            cache[self.attrname] = slot = Slot(getattr(instance, '_queue_' + self.ssname))
        return slot


class SignalProperty(Generic[_T]):
    def __init__(self, name):
        self.ssname = name
        self.attrname = None

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same signal to two different names "
                f"({self.attrname!r} and {name!r})."
            )
        elif name not in [self.ssname, '_' + self.ssname]:
            raise TypeError(
                "Cannot assign signal name different from signalslot name "
                f"({self.ssname!r} != {name})")

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use signal instance without calling __set_name__ on it.")

        cache = instance.__dict__
        signal = cache.get(self.attrname)
        if signal is None:
            queue = getattr(instance, '_queue_' + self.ssname, None)
            if queue is None:
                queue = asyncio.Queue()
                setattr(instance, '_queue_' + self.ssname, queue)
            cache[self.attrname] = signal = Signal(getattr(instance, '_queue_' + self.ssname))
        assert isinstance(signal, Signal)
        return signal


def signal_slot(name: str) -> tuple[SignalProperty[_T], SlotProperty[_T]]:
    return SignalProperty[_T](name), SlotProperty[_T](name)
