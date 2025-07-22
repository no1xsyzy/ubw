from __future__ import annotations

import abc
import asyncio
import functools
import warnings
from collections.abc import Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Self, Callable, TypeAlias, Annotated, Union

from pydantic import BaseModel, model_validator, TypeAdapter, Field

Collector: TypeAlias = 'Callable[[BaseActor], None]'
_collector: ContextVar[Collector | None] = ContextVar('_collector', default=None)


@contextmanager
def collect():
    collected: list[BaseActor] = []
    token = _collector.set(collected.append)
    try:
        yield collected
    finally:
        _collector.reset(token)


def actor_tree(actor):
    return {
        'name': actor.name,
        'type': actor.__class__.__qualname__,
        'owned_actors': [actor_tree(a) for a in actor.owned_actors]
    }


class BaseActor(BaseModel, abc.ABC):
    name: str

    _main_task: asyncio.Task | None = None
    _owned_actors: Sequence[BaseActor] = ()

    @model_validator(mode='wrap')
    @classmethod
    def actor_collect_me(cls, data, handler) -> Self:
        with collect() as collected:
            self = handler(data)
        self._owned_actors = [*self._owned_actors, *collected]
        if callable(collector := _collector.get()):
            collector(self)
        return self

    @property
    def actor_owned_actors(self):
        return self._owned_actors[:]

    def actor_tree(self):
        return {
            'name': self.name,
            'type': self.__class__.__qualname__,
            'owned_actors': [actor_tree(a) for a in self._owned_actors[:]]
        }

    def start(self):
        if self._main_task is not None:
            warnings.warn(f'actor {self.name} start() but already started')
            return
        self._main_task = asyncio.create_task(self.main())
        for actor in self._owned_actors:
            actor.start()

    def stop(self):
        if self._main_task is None:
            warnings.warn(f'actor {self.name} stop() but not yet started')
            fut = asyncio.Future()
            fut.set_result(None)
            return fut
        task = self._main_task
        self._main_task = None
        task.cancel('stop')
        for actor in self._owned_actors:
            actor.stop()
        return task

    @abc.abstractmethod
    async def main(self):
        pass

    async def join(self):
        await asyncio.gather(*((actor.join() for actor in self._owned_actors)))

    async def close(self):
        for actor in self._owned_actors:
            await actor.close()


@functools.cache
def get_subclass_type_adapter(actor_class: type[BaseActor]):
    return TypeAdapter(Annotated[Union[*actor_class.__subclasses__()], Field(discriminator='type')])


def create_actor(actor_class: type[BaseActor], config):
    ta = get_subclass_type_adapter(actor_class)
    return ta.validate_python(config)
