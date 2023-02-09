from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from blivedm import BaseHandler, BLiveClient, models
from blivedm.models import CommandModel


class Output(str, Enum):
    csv = 'csv'
    log = 'log'


class Fetch(BaseModel):
    output: Optional[list[Output]] = None
    prefix: Optional[list[str]] = None
    uids: Optional[list[int]] = None
    reverse: bool = False
    skip: int = 0
    types: list[str] = Field(default_factory=lambda: ['danmu_msg'])

    def handle_me(self, model: CommandModel):
        if model.cmd.lower() not in self.types:
            return self._unmatch()
        if self.prefix is not None:
            if isinstance(model, models.DanmakuCommand) and \
                    all(not model.info.msg.startswith(p) for p in self.prefix):
                return self._unmatch()
        if self.uids is not None:
            if isinstance(model, models.DanmakuCommand) and \
                    not model.info.uid not in self.uids:
                return self._unmatch()
        return self._matched()

    def _unmatch(self):
        if self.reverse:
            return self.output, self.skip

    def _matched(self):
        if not self.reverse:
            return self.output, self.skip


class Room(BaseModel):
    room_id: int
    fetch: list[Fetch]

    def handle_me(self, model: CommandModel):
        skip = 0
        output = set()
        for f in self.fetch:
            if skip > 0:
                skip -= 1
            else:
                out, skip = f.handle_me(model)
                output += out
        return output


class Config(BaseModel):
    room: Room
