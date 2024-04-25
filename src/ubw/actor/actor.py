from __future__ import annotations

import abc
import asyncio
import warnings
from functools import wraps, partial, cached_property
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
    time_limit_per_loop: int | None = None

    async def _init(self):
        pass

    @abc.abstractmethod
    async def _loop(self):
        ...

    async def _finalize(self):
        pass

    async def _error_handle(self, exc):
        pass

    async def _run(self: BaseActor):
        try:
            await self._init()
            while True:
                try:
                    if self.time_limit_per_loop is not None:
                        with asyncio.timeout(self.time_limit_per_loot):
                            await self._loop()
                    else:
                        await self._loop()
                except Exception as e:
                    await self._error_handle(e)
        finally:
            await self._finalize()


class JustStartOtherActorsMixin(BaseActor, abc.ABC):
    async def _init(self):
        pass

    async def _run(self):
        await self._init()


def behaviour(f=None, /, name=None):
    if f is None:
        return partial(behaviour)

    if name is None:
        if f.__name__ == '<lambda>':
            raise ValueError('define behaviour with lambdas must have name set')
        else:
            name = f.__name__

    @wraps(f)
    def behaviour_wrapper(self: BehaviourActor, *args, **kwargs):
        self._bind_name(name, f)
        try:
            self._behaviour_call_queue.put_nowait((f.__name__, args, kwargs))
            return True
        except asyncio.QueueFull:
            return False

    def threadsafe(self: BehaviourActor, *args, **kwargs):
        self._loop.call_soon_threadsafe(self._behaviour_call_queue.put, (f.__name__, args, kwargs))
        return

    behaviour_wrapper.threadsafe = threadsafe
    behaviour_wrapper.__name__ = name

    return behaviour_wrapper


be = behaviour


class BehaviourActor(InitLoopFinalizeMixin, BaseActor):
    _behaviour_call_queue: asyncio.Queue

    @cached_property
    def _msg_registry(self):
        return {}

    def _bind_name(self, name, func):
        if name in self._msg_registry:
            if self._msg_registry[name] is not func:
                raise ValueError(f'behaviour {name} is defined multiple times')
        else:
            self._msg_registry[name] = func

    async def _init(self):
        self._behaviour_call_queue = asyncio.Queue()
        self._loop = asyncio.get_running_loop()

    async def _loop(self):
        f, args, kwargs = await self._behaviour_call_queue.get()
        if asyncio.iscoroutinefunction(f):
            await f(self, *args, **kwargs)
        else:
            f(self, *args, **kwargs)
