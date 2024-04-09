import asyncio
import pkgutil
import warnings
from typing import NamedTuple, Callable
from weakref import ref


# _get_target copied from unittest.mock
def _get_target(target):
    try:
        target, attribute = target.rsplit('.', 1)
    except (TypeError, ValueError, AttributeError):
        raise TypeError(
            f"Need a valid target to patch. You supplied: {target!r}")
    return pkgutil.resolve_name(target), attribute


class Call(NamedTuple):
    target: 'AsyncMock | SyncMock | AsyncPatcher | SyncPatcher'
    args: tuple
    kwargs: dict
    fut: asyncio.Future | None

    def assert_match_call(self, *args, **kwargs):
        assert args == self.args and kwargs == self.kwargs

    def assert_complex_match(self, *args, **kwargs):
        assert len(args) == len(self.args)
        for ea, aa in zip(args, self.args):
            if isinstance(ea, (AsyncMock, SyncMock, AsyncPatcher, SyncPatcher)):
                assert ea is aa
            elif callable(ea):
                assert ea(aa)
            else:
                assert ea == aa
        assert kwargs.keys() == self.kwargs.keys()
        for k in kwargs.keys():
            ev = kwargs[k]
            av = self.kwargs[k]
            if isinstance(ev, (AsyncMock, SyncMock, AsyncPatcher, SyncPatcher)):
                assert ev is av
            elif callable(ev):
                assert ev(av)
            else:
                assert ev == av

    def set_result(self, result):
        assert self.fut is not None, 'cannot set_result() on sync call, use returner instead'
        self.fut.set_result(result)

    def set_exception(self, exc):
        assert self.fut is not None, 'cannot set_exception() on sync call, use returner instead'
        self.fut.set_exception(exc)


def returns(x=None):
    def returner(*args, **kwargs):
        return x

    return returner


class AsyncPatcher:
    def __init__(self, story: 'AsyncStoryline', target: str):
        ref_story = ref(story, self.__ref_cb)
        self.__story = ref_story
        self.__target = target
        self.__active = False
        self.__original = None

    def __ref_cb(self, wr):
        if self.__active:
            self.__deactivate()

    def __getattr__(self, item):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            subp = story.add_async_patch(self.__target + "." + item)
            setattr(self, item, subp)
            return subp

    def __activate(self):
        obj, attribute = _get_target(self.__target)
        self.__active = True
        self.__original = getattr(obj, attribute)
        setattr(obj, attribute, self)

    def __deactivate(self):
        obj, attribute = _get_target(self.__target)
        assert getattr(obj, attribute) is self, "monkey patch is crossed over"
        setattr(obj, attribute, self.__original)
        self.__original = None
        self.__active = False

    def __del__(self):
        if self.__active:
            self.__deactivate()

    def __enter__(self):
        self.__activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__deactivate()

    async def __call__(self, *args, **kwargs):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            fut = asyncio.Future()
            await story.put(Call(self, args, kwargs, fut))
            return await fut


class SyncPatcher:
    def __init__(self, story: 'AsyncStoryline', target: str, returner):
        ref_story = ref(story, self.__ref_cb)
        self.__story = ref_story
        self.__target = target
        self.__active = False
        self.__original = None
        self.__returner = returner

    def __ref_cb(self, wr):
        if self.__active:
            self.__deactivate()

    def __getattr__(self, item):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            subp = story.add_sync_patch(self.__target + "." + item)
            setattr(self, item, subp)
            return subp

    def __activate(self):
        obj, attribute = _get_target(self.__target)
        self.__active = True
        self.__original = getattr(obj, attribute)
        setattr(obj, attribute, self)

    def __deactivate(self):
        obj, attribute = _get_target(self.__target)
        assert getattr(obj, attribute) is self, "monkey patch is crossed over"
        setattr(obj, attribute, self.__original)
        self.__original = None
        self.__active = False

    def __del__(self):
        if self.__active:
            self.__deactivate()

    def __enter__(self):
        self.__activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__deactivate()

    def __call__(self, *args, **kwargs):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            story.put_nowait(Call(self, args, kwargs, None))
            return self.__returner(*args, **kwargs)


class SyncMock:
    def __init__(self, story: 'AsyncStoryline', returner):
        ref_story = ref(story)
        self.__story = ref_story
        self.__active = False
        self.__original = None
        self.__returner = returner
        self.__target = str(id(self))

    def __getattr__(self, item):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            subp = story.add_sync_mock()
            setattr(self, item, subp)
            return subp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *args, **kwargs):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            story.put_nowait(Call(self, args, kwargs, None))
            return self.__returner(*args, **kwargs)


class AsyncMock:
    def __init__(self, story: 'AsyncStoryline'):
        ref_story = ref(story)
        self.__story = ref_story
        self.__active = False
        self.__original = None
        self.__target = str(id(self))

    def __getattr__(self, item):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            subp = story.add_async_mock()
            setattr(self, item, subp)
            return subp

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __call__(self, *args, **kwargs):
        story: AsyncStoryline | None = self.__story()
        if story is not None:
            fut = asyncio.Future()
            await story.put(Call(self, args, kwargs, fut))
            return await fut


class AsyncStoryline:
    def __init__(self):
        self._patches: list[AsyncPatcher | SyncPatcher | AsyncMock | SyncMock] = []
        self._es = {}
        self._queue = asyncio.Queue[Call]()
        self._old_calls = list[Call]()
        self._waiting_list = list[Callable[[Call | None], bool]]()
        self._polling_task: asyncio.Task | None = None
        self._active = False

    def __enter__(self):
        self._active = True
        self._polling_task = asyncio.create_task(self._poll())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in self._patches:
            p.__exit__(exc_type, exc_val, exc_tb)
        self._active = False
        self._polling_task.cancel()
        if self._waiting_list:
            warnings.warn(f'{len(self._waiting_list)} get_call() still waiting, stopping them')
            for w in self._waiting_list:
                w(None)
        self._patches = []

    def add_async_patch(self, target, patch_class=AsyncPatcher):
        patch = patch_class(self, target)
        self._patches.append(patch)
        entered = patch.__enter__()
        self._es[target] = entered
        return entered

    def add_sync_patch(self, target, patch_class=SyncPatcher):
        def deco(returner):
            if not callable(returner):
                raise TypeError("add_sync_patch must be used as function decorator")
            patch = patch_class(self, target, returner)
            self._patches.append(patch)
            entered = patch.__enter__()
            self._es[target] = entered
            return entered

        return deco

    def add_sync_mock(self, mock_class=SyncMock):
        def deco(returner):
            if not callable(returner):
                raise TypeError("add_sync_mock must be used as function decorator")
            mock = mock_class(self, returner)
            self._patches.append(mock)
            entered = mock.__enter__()
            return entered

        return deco

    def add_async_mock(self, mock_class=AsyncMock):
        mock = mock_class(self)
        self._patches.append(mock)
        entered = mock.__enter__()
        return entered

    def __getitem__(self, item):
        return self._es[item]

    async def _poll(self):
        while True:
            c = await self._queue.get()
            mw = None
            for w in self._waiting_list:
                if w(c):
                    mw = w
                    break
            if mw is not None:
                self._waiting_list.remove(mw)
            else:
                self._old_calls.append(c)

    async def put(self, v: Call):
        if not self._active:
            raise RuntimeError('put() out of scope, prohibited')
        await self._queue.put(v)

    def put_nowait(self, v: Call):
        if not self._active:
            raise RuntimeError('put() out of scope, prohibited')
        self._queue.put_nowait(v)

    async def get_call(self, *, target=None, f=None, _debug=False) -> Call:
        if f not in ['async', 'sync', None]:
            raise ValueError(f'f must be one of `async` or `sync`, got {f!r}')
        if target is not None and f is not None:
            if isinstance(target, (AsyncMock, AsyncPatcher)) ^ (f == 'async'):
                raise TypeError(f'{target!r} is {target.__class__.__name__} but require {f} function')

        def checker(_call):
            if target is not None and target is not _call.target:
                return False
            if f == 'async' and _call.fut is None:
                return False
            if f == 'sync' and _call.fut is not None:
                return False
            return True

        p = None
        for i, c in enumerate(self._old_calls):
            if checker(c):
                p = i
                break
        if p is not None:
            return self._old_calls.pop(p)

        f = asyncio.Future()

        if not self._active:
            raise RuntimeError('get_call() out of scope and impossible for more calls')

        def waiting(call: Call | None):
            if call is None:
                f.set_exception(RuntimeError)
                return
            if checker(call):
                f.set_result(call)
                return True

        self._waiting_list.append(waiting)
        return await f


def test_storyline():
    async def main(async_mock, sync_mock):
        import rich

        print(' ' * 75 + 'before await asyncio.sleep(0.7)', flush=True)
        res = await asyncio.sleep(0.7)
        print(' ' * 75 + f'after await asyncio.sleep(0.7), got {res=}', flush=True)

        print(' ' * 75 + 'before await asyncio.sleep(3600)', flush=True)
        res = await asyncio.sleep(3600)
        print(' ' * 75 + f'after await asyncio.sleep(3600), got {res=}', flush=True)

        print(' ' * 75 + "before rich.print('abc')", flush=True)
        res = rich.print('abc')
        print(' ' * 75 + f"after rich.print('abc'), got {res=}", flush=True)

        print(' ' * 75 + "before async_mock('am')", flush=True)
        res = await async_mock('am')
        print(' ' * 75 + f"after async_mock('am'), got {res=}",
              flush=True)

        print(' ' * 75 + "before sync_mock('sm')", flush=True)
        res = sync_mock('sm')
        print(' ' * 75 + f"after sync_mock('sm'), got {res=}", flush=True)

    async def wrapper():
        with AsyncStoryline() as p:
            ass = p.add_async_patch('asyncio.sleep')

            @p.add_sync_patch('rich.print')
            def rp(j):
                return 'you called rp'

            am = p.add_async_mock()

            @p.add_sync_mock()
            def sm(j):
                return j * 5

            print(f"{ass=}")
            print(f"{asyncio.sleep=}")
            print(f"{rp=}")
            print(f"{am=}")
            print(f"{sm=}")
            print()
            print("=" * 20)
            print()

            t = asyncio.create_task(main(am, sm))

            r, a, k, f = await p.get_call()
            assert r is ass
            print(r, a, k, flush=True)
            f.set_result(42)

            r, a, k, f = await p.get_call()
            assert r is ass
            print(r, a, k, flush=True)
            f.set_result(80)

            r, a, k, f = await p.get_call()
            # assert r is rp
            print(r, a, k, flush=True)

            r, a, k, f = await p.get_call()
            assert r is am
            print(r, a, k, flush=True)
            f.set_result('you there?')

            r, a, k, f = await p.get_call()
            assert r is sm
            print(r, a, k, flush=True)

            await t
            print()
            print("=" * 20)
            print()
            print(f"{ass=}")
            print(f"{asyncio.sleep=}")
            print(f"{rp=}")
            print(f"{am=}")
            print(f"{sm=}")
        print(asyncio.sleep)

    asyncio.run(wrapper())


if __name__ == '__main__':
    test_storyline()
