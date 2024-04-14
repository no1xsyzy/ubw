from __future__ import annotations

import abc
import asyncio
import warnings
from typing import Annotated, Union, Type, Literal

from pydantic import BaseModel, Field, TypeAdapter, ConfigDict

from .signalslot import Signal, SlotProperty, SignalProperty, signal_slot

__all__ = (
    'BaseActor',
    'JustStartOtherActorsMixin', 'InitLoopFinalizeMixin',
    'signal_slot', 'Literal',
)


async def _stop_and_ignore_cancelled_error(t: asyncio.Task):
    if t.cancel():
        try:
            await t
        except asyncio.CancelledError:
            return True
    else:
        return False


class BaseActor(BaseModel, abc.ABC):
    model_config = ConfigDict(ignored_types=(SignalProperty, SlotProperty))

    role: str

    _task: asyncio.Task | None = None

    @classmethod
    def leaf_subclasses(cls):
        result = []
        for c in cls.__subclasses__():
            if c.model_fields['role'].annotation is not str:
                result.append(c)
            result.extend(c.leaf_subclasses())
        return result

    @classmethod
    def make_discriminator(cls) -> Type[Union[BaseActor]]:
        return Annotated[Union[*cls.leaf_subclasses()], Field(discriminator='role')]

    @classmethod
    def make_adapter(cls) -> TypeAdapter[BaseActor]:
        return TypeAdapter(cls.make_discriminator())

    def nested_actors(self) -> list[BaseActor]:
        result = []
        for f in self.model_fields.keys():
            a = getattr(self, f)
            if isinstance(a, BaseActor):
                result.append(a)
        return result

    def signal_connects(self):
        result = []
        for f in dir(self):
            s = getattr(self, f, None)
            if isinstance(s, Signal) and s.connect_task is not None:
                result.append(s.connect_task)
        return result

    @abc.abstractmethod
    async def _run(self):
        ...

    async def start(self):
        if self._task is not None:
            return warnings.warn(f"{self.role} is already running")
        self._task = asyncio.create_task(self._run())
        for a in self.nested_actors():
            await a.start()

    async def join(self):
        if self._task is None:
            return warnings.warn(f"{self.role} is stopped, cannot join()")
        await asyncio.shield(asyncio.gather(self._task, *(a.join() for a in self.nested_actors())))

    async def stop(self):
        task = self._task
        self._task = None
        if task is None:
            return warnings.warn(f"{self.role} is stopped, cannot stop() again")

        await asyncio.gather(
            _stop_and_ignore_cancelled_error(task),
            *(_stop_and_ignore_cancelled_error(c) for c in (self.signal_connects())),
            *(a.stop() for a in (self.nested_actors())),
        )

    async def close_one(self):
        pass

    async def close(self):
        await asyncio.gather(self.close_one(), *(a.close() for a in self.nested_actors()), return_exceptions=True)

    async def stop_and_close(self):
        try:
            await self.stop()
        finally:
            await self.close()


class InitLoopFinalizeMixin(BaseActor, abc.ABC):
    async def _init(self):
        pass

    @abc.abstractmethod
    async def _loop(self):
        ...

    async def _finalize(self):
        pass

    async def _run(self: BaseActor):
        try:
            await self._init()
            while True:
                await self._loop()
        finally:
            await self._finalize()


class JustStartOtherActorsMixin(BaseActor, abc.ABC):
    async def _init(self):
        pass

    async def _run(self):
        await self._init()
