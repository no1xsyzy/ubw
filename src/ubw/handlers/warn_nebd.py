import abc
import importlib.resources
import re
from collections import Counter
from datetime import datetime, timedelta, date
from typing import Annotated

from pydantic import BaseModel, Field, TypeAdapter

from ubw.ui.stream_view import *
from ._base import *

check_in_words_txt = importlib.resources.files('ubw.handlers') / 'check_in_words.txt'

KAOMOJIS = [kmj for kmj in (check_in_words_txt.read_text(encoding='utf-8')).splitlines()
            if kmj and not (kmj.startswith('<comment>') and kmj.endswith('</comment>'))]

RE_KAOMOJIS = [re.escape(kaomoji) for kaomoji in KAOMOJIS]

RE_SHITTING = re.compile('|'.join([
    *RE_KAOMOJIS,
    r"^\d{1,3}$",
    r"^[a-zA-Z]$",
]))


def is_shitting(msg):
    return bool(RE_SHITTING.search(msg))


def effective_day(dt: datetime) -> date:
    return (dt - timedelta(hours=6)).date()


class InteractCheckerABC(BaseModel, abc.ABC):
    method: str

    @abc.abstractmethod
    def see_entrance(self):
        pass

    @abc.abstractmethod
    def shift_danmaku(self, c: models.DanmakuCommand) -> tuple[list[str], int]:
        pass


class ExpDecayInteract(InteractCheckerABC):
    method: Literal['exp_decay'] = 'exp_decay'

    last_t: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    score_now: float = 0.0

    def see_entrance(self):
        pass

    def shift_danmaku(self, c: models.DanmakuCommand) -> tuple[list[str], int]:
        pass


class LastInteract(InteractCheckerABC):
    method: Literal['last'] = 'last'

    memory_limit: int = 20

    # state
    entrance: datetime | None = None
    danmu: datetime | None = None
    latest_danmakus: list[models.DanmakuCommand] = []
    latest_scores: list[int] = []
    latest_problems: list[list[str]] = []

    def see_entrance(self):
        self.entrance = datetime.now().astimezone()

    def shift_danmaku(self, c: models.DanmakuCommand) -> tuple[list[str], int]:
        problems = []
        msg = c.info.msg
        self.latest_danmakus.append(c)
        g = 0
        while len(self.latest_danmakus) > self.memory_limit:
            self.latest_danmakus.pop(0)
            g += 1

        score = 0
        if is_shitting(msg):
            problems.append('shitting')
            score += 5

        if c.info.mode_info.extra.emoticon_unique:
            problems.append('emoticon')
            score += 3

        if (emot := c.info.mode_info.extra.emots) is not None:
            for emot in emot.keys():
                if emot in msg:
                    problems.append("emot")
                    score += 3
                    break

        counter = Counter(dmk.info.msg for dmk in self.latest_danmakus)
        repeating_ratio = counter[msg] / len(counter)
        if repeating_ratio > 1:
            problems.append("repeating")
            score += 5
        else:
            problems.append(f"({repeating_ratio=:.2f})")

        now = datetime.now().astimezone()
        if self.entrance is None:
            problems.append("no entrance")
            score += 3
        else:
            ago = now - self.entrance
            if ago > timedelta(days=2):
                problems.append("entrance > 2d")
            elif ago <= timedelta(hours=1):
                pass
            elif effective_day(now) != effective_day(self.entrance):
                problems.append("no entrance today")
            else:
                problems.append("entrance > 1h")

        if self.danmu is None:
            problems.append("first danmu")
        else:
            ago = now - self.danmu
            if ago > timedelta(days=2):
                problems.append("danmu > 2d")
            elif ago < timedelta(seconds=1):
                problems.append("<1s")
                score += 2
            elif ago < timedelta(minutes=1):
                problems.append("<1min")
                score *= 2
            elif ago <= timedelta(hours=1):
                pass
            elif effective_day(now) != effective_day(self.danmu):
                problems.append("first danmu today")
            else:
                problems.append("danmu > 1h")

        self.latest_scores.append(score)
        self.latest_scores[:g] = []
        self.danmu = now

        return problems, sum(self.latest_scores)


InteractChecker = Annotated[ExpDecayInteract | LastInteract, Field(discriminator='method')]
IC_ADAPTER = TypeAdapter(InteractChecker)


def make_ic(method):
    return IC_ADAPTER.validate_python({'method': method})


class WarnNoEntranceButDanmakuHandler(BaseHandler):
    cls: Literal['warn_nebd'] = 'warn_nebd'

    method: str = 'last'

    ui: StreamView = Richy()
    owned_ui: bool = True

    _ui_started: bool = False

    # ui: Annotated[StreamView, di(factory=Richy), sub_actor()]
    # ui: StreamView @ di(factory=Richy) @ sub_actor()

    ics: dict[int, InteractChecker] = {}

    # ics: Annotated[dict[int, LastInteract], store()]
    # ics: dict[int, LastInteract] @ store()

    async def start(self, client):
        if self.owned_ui and self.ui is not None and not self._ui_started:
            await self.ui.start()

    def last_interact_of(self, uid) -> InteractChecker:
        if uid not in self.ics:
            self.ics[uid] = make_ic(self.method)
        return self.ics[uid]

    async def on_danmu_msg(self, client, message: models.DanmakuCommand):
        uname = message.info.uname
        msg = message.info.msg
        uid = message.info.uid
        room_id = client.room_id
        if message.info.mode_info.user is not None:
            face = message.info.mode_info.user.base.face
        else:
            face = ''
        interact = self.last_interact_of(uid)
        segments = [
            ColorSeeSee(text=f"[{room_id}] "),
            User(name=uname, uid=uid, face=face),
            PlainText(text=f": "),
            PlainText(text=msg),
        ]
        problems, score = interact.shift_danmaku(message)
        for problem in problems:
            segments.append(ColorSeeSee(text="[" + problem + "]"))
        segments.append(PlainText(text=f"{score=}"))

        await self.ui.add_record(Record(segments=segments, time=message.ct))

    async def on_interact_word(self, client, model):
        uid = model.data.uid
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            User(name=model.data.uname, uid=uid, face=model.data.uinfo.base.face),
            PlainText(text=model.MSG_NAME[model.data.msg_type]),
            PlainText(text="了直播间"),
        ], time=model.ct, importance=0))
        if model.data.msg_type == 1:  # 进入
            self.last_interact_of(uid).see_entrance()
