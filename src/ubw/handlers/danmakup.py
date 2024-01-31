import logging
import math
import re
from functools import cached_property

import rich
from pydantic import field_validator, model_validator
from rich.markup import escape

from ubw.ui import Record, PlainText, User, RoomTitle, UI, ColorSeeSee
from ._base import *
from ..models import blive as models

KAOMOJIS = [
    "(⌒▽⌒)",
    "（￣▽￣）",
    "(=・ω・=)",
    "(｀・ω・´)",
    "(〜￣△￣)〜",
    "(･∀･)",
    "(°∀°)ﾉ",
    "(￣3￣)",
    "╮(￣▽￣)╭",
    "_(:3」∠)_",
    "_(:3ゝ∠)_",  # slightly different :-(
    "(^・ω・^ )",
    "(●￣(ｴ)￣●)",
    "ε=ε=(ノ≧∇≦)ノ",
    "⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄",
    "←◡←",
    "^v^",
    "OvO",
    "( ☉д⊙)",
    "(╯°口°)╯",
    "o(￣ヘ￣o＃)",
    "|•'▿'•)✧",
    "( TロT)σ",
    "ᕕ( ´Д` )ᕗ",
    "(●'◡'●)ﾉ♥",
    "|ω・）",
    "੭ ᐕ)੭*⁾⁾",
    "( ｣ﾟДﾟ)｣＜",
    "(⁠｡⁠•̀⁠ᴗ⁠-⁠)⁠✧",
    "վ'ᴗ' ի",
    "QAQ",
    "( ◡‿◡)",
    "( *・ω・)✄",
]


class TokenEntropy:
    def __init__(self, dispersion=0.9, disappear=0.01):
        self.dispersion = dispersion
        self.disappear = disappear
        self.generation = 0
        self.cgs: dict[str, tuple[float, int]] = {}
        self.total = 0

    def get_current(self, token: str) -> float:
        if token not in self.cgs:
            return 0
        c, g = self.cgs[token]
        c = c * (self.dispersion ** (self.generation - g))
        if c < self.disappear:
            del self.cgs[token]
            self.total -= c
            return 0
        return c

    def calculate_and_add_tokens(self, tokens: list[str]):
        self.generation += 1
        self.total = self.total * self.dispersion + len(tokens)
        entropy = 0
        for token in tokens:
            c = self.get_current(token)
            c += 1.
            entropy += -math.log2(c / self.total)
            self.cgs[token] = c, self.generation
        return entropy

    def cleanup(self):
        pass


class RichClientAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['markup'] = True
        return msg, kwargs


logger = RichClientAdapter(logging.getLogger('danmakup'), {})


class DanmakuPHandler(BaseHandler):
    cls: Literal['danmakup'] = 'danmakup'
    ignore_danmaku: re.Pattern | None = None

    ignore_rate: float = 0.0
    dim_rate: float = 0.25

    show_interact_word: bool = False
    test_flags: list[str] = []
    ui: UI | None = None

    @model_validator(mode='after')
    def ignore_less_than_dim(self):
        if self.ignore_rate > self.dim_rate:
            raise ValueError('dim rate should not be less than ignore rate')
        return self

    @field_validator('test_flags', mode='before')
    @classmethod
    def split_flags(cls, v):
        if isinstance(v, str):
            v = v.split(',')
        return v

    @cached_property
    def kaomojis(self):
        return set(KAOMOJIS)

    @property
    def kaomoji_regex(self):
        return re.compile('|'.join(re.escape(kaomoji) for kaomoji in self.kaomojis))

    @cached_property
    def entropy(self):
        return TokenEntropy()

    @cached_property
    def tokenizer(self):
        import jieba
        tok = jieba.Tokenizer()
        for kmj in KAOMOJIS:
            tok.add_word(kmj, tag='e')
            tok.suggest_freq(kmj, True)
        return tok

    def trivial_rate(self, info: models.danmu_msg.DanmakuInfo) -> float:
        if self.ignore_danmaku is not None and self.ignore_danmaku.match(info.msg):
            return -1
        if info.mode_info.extra.emoticon_unique:  # 单一表情
            return 0.1
        msg = info.msg
        msg = self.kaomoji_regex.sub("\ue000\ue000", msg)  # U+E000 is in private use area
        msg = msg.replace("打卡", "\ue000")
        msg = msg.replace(".", "\ue000", 1)
        if info.mode_info.extra.emots is not None:
            for emot in info.mode_info.extra.emots.keys():
                msg = msg.replace(emot, "\ue000")
        return len(msg.replace("\ue000", "")) / len(msg)

    async def on_danmu_msg(self, client, message: models.DanmakuCommand):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id
        trivial_rate = self.trivial_rate(message.info)

        # ==== testing: entropy ====
        if 'entropy' in self.test_flags:
            tokens = []
            if message.info.mode_info.extra.emots is not None:
                self.kaomojis.update(message.info.mode_info.extra.emots.keys())
            for s in re.split('(' + '|'.join(re.escape(kaomoji) for kaomoji in self.kaomojis) + ')', msg):
                if s == "":
                    pass
                elif s in self.kaomojis:
                    tokens.append(s)
                else:
                    tokens.extend(self.tokenizer.lcut(s))
            entropy = self.entropy.calculate_and_add_tokens(tokens)
            if self.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f": "),
                    PlainText(text=f"{tokens}"),
                    PlainText(
                        text=f" ({entropy=:.3f}, {entropy/len(tokens)=:.3f}, {trivial_rate=:.3f})"),
                ]))
            else:
                rich.print(
                    rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): {escape(str(tokens))}"
                    f" ({entropy=:.3f}, {entropy/len(tokens)=:.3f}, {trivial_rate=:.3f})")
            return
        # ==== testing: entropy ====

        if trivial_rate < self.ignore_rate:
            pass
        elif trivial_rate < self.dim_rate:
            if self.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f": "),
                    PlainText(text=msg),
                    PlainText(text=f" (trivial {trivial_rate})"),
                ]))
            else:
                rich.print(
                    rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [grey]{escape(msg)}[/]")
        else:
            if self.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f"说: "),
                    PlainText(text=msg),
                ]))
            else:
                rich.print(
                    rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [bright_white]{escape(msg)}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id

        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"直播间信息变更"),
                RoomTitle(title=title, room_id=room_id),
                PlainText(text=f"，分区：{parent_area_name}/{area_name}"),
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] "
                f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_summary(self, client, summary):
        if self.ui is None:
            rich.print(
                rf"\[{summary.t.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{client.room_id}[/]] "
                rf"{summary.msg} ({summary.raw.cmd})"
            )

    async def on_warning(self, client, message: models.WarningCommand):
        room_id = client.room_id
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"受到警告 {message.msg}"),
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] [white on red]{message}[/]")

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=uname, uid=message.data.uid),
                PlainText(text=f"[¥{price}]: {msg}")
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] {uname} \[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="用户被封禁"),
                User(name=message.data.uname, uid=message.data.uid),
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] "
                f"[red]用户 {message.data.uname}（uid={message.data.uid}）被封禁[/]")

    async def on_live(self, client, message):
        room_id = client.room_id
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播开始"),
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] "
                "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Square For Stop}\N{VS16}直播结束"),
            ]))
        else:
            rich.print(
                rf"\[{message.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")

    async def on_interact_word(self, client, model):
        if not self.show_interact_word:
            return
        room_id = client.room_id
        c = ["", "进入", "关注", "分享", "特别关注", "互相关注"]
        if self.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=model.data.uname, uid=model.data.uid),
                PlainText(text=c[model.data.msg_type]),
                PlainText(text="了直播间"),
            ]))
        else:
            rich.print(
                rf"\[{model.ct.strftime('%Y-%m-%d %H:%M:%S')}] "
                rf"\[[bright_cyan]{room_id}[/]] 用户 {model.data.uname}（uid={model.data.uid}）"
                rf"{c[model.data.msg_type]}了直播间")
