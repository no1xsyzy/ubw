import abc
import asyncio

import pytest

from ubw.actor import *


class Adder(InitLoopFinalizeMixin, BaseActor):
    role: Literal['adder'] = 'adder'
    _x, x = signal_slot('x')  # input slot
    _y, y = signal_slot('y')  # input slot
    z, _z = signal_slot('z')  # output signal

    async def _loop(self):
        xv = await self._x.get()
        yv = await self._y.get()
        zv = xv + yv
        await self._z.put(zv)


class OneInOneOut(BaseActor, abc.ABC):
    _i, i = signal_slot('i')  # input slot
    o, _o = signal_slot('o')  # output signal


class Functional(InitLoopFinalizeMixin, OneInOneOut):
    @abc.abstractmethod
    def func(self, x): ...

    async def _loop(self):
        xv = await self._i.get()
        yv = self.func(xv)
        await self._o.put(yv)


class Multiplier(Functional):
    role: Literal['multiplier'] = 'multiplier'
    by: float = 2

    def func(self, x):
        return x * self.by


class Compose(JustStartOtherActorsMixin, OneInOneOut):
    role: Literal['compose'] = 'compose'

    actors: list[OneInOneOut.make_discriminator()]

    def nested_actors(self) -> list[BaseActor]:
        return super().nested_actors() + self.actors

    async def _init(self):
        last_sig = self._i
        for a in self.actors:
            last_sig.connect(a.i)
            last_sig = a.o
        last_sig.connect(self._o)
        await super()._init()


class AddAndThen(JustStartOtherActorsMixin):
    role: Literal['addandthen'] = 'addandthen'
    _x, x = signal_slot('x')  # input slot
    _y, y = signal_slot('y')  # input slot
    z, _z = signal_slot('z')  # output signal

    add: Adder
    then: OneInOneOut.make_discriminator()

    async def _init(self):
        self._x.connect(self.add.x)
        self._y.connect(self.add.y)
        self.add.z.connect(self.then.i)
        self.then.o.connect(self._z)


@pytest.mark.asyncio
async def test_actor():
    adder1 = Adder()
    adder2 = Adder()
    adder1.start()
    adder2.start()
    await adder1.x.put(1)
    await adder2.x.put(2)
    await adder2.y.put(4)
    await adder1.y.put(8)
    res1 = await adder1.z.get()
    res2 = await adder2.z.get()
    assert res1 == 9
    assert res2 == 6

    await adder1.stop()
    await adder2.stop()


@pytest.mark.asyncio
async def test_connect():
    adder = Adder()
    multi = Multiplier(by=1.5)
    adder.start()
    multi.start()
    await adder.x.put(3)
    await adder.y.put(4)
    adder.z.connect(multi.i)
    res = await multi.o.get()
    assert res == 7 * 1.5
    await adder.stop()
    await multi.stop()


@pytest.mark.asyncio
async def test_nested():
    adapter = BaseActor.make_adapter()
    comp = adapter.validate_python({
        'role': 'addandthen',
        'add': {},
        'then': {
            'role': 'compose',
            'actors': [
                {'role': 'multiplier', 'by': 3},
                {'role': 'multiplier', 'by': 2},
                {'role': 'multiplier', 'by': 7},
            ],
        }
    })
    comp.start()
    await comp.x.put(0.3)
    await comp.y.put(0.7)
    res = await comp.z.get()
    assert res == 42

    t = asyncio.create_task(comp.join())
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    await comp.stop_and_close()
    with pytest.raises(asyncio.CancelledError):
        await t
