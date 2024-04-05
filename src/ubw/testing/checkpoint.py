import asyncio


class Checkpoint:
    def __init__(self):
        self._future = asyncio.Future()
        self._more_side_effect = None

    def back_conn(self, mock):
        def decorator(f):
            self._more_side_effect = f
            return f

        mock.side_effect = self.side_effect
        return decorator

    def reach(self, val=None):
        if not self._future.done():
            self._future.set_result(val)

    def side_effect(self, *args, **kwargs):
        self.reach()
        return self._more_side_effect(*args, **kwargs)

    def is_reached(self):
        return self._future.done()

    def __await__(self):
        yield from self._future.__await__()
