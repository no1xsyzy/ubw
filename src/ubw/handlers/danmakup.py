import logging
import math
import re
from functools import cached_property

import pydantic
from rich.markup import escape

import blivedm
from ubw.ui import Record, PlainText, User, RoomTitle, UI, ColorSeeSee

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


def try_compile(cls, reg: re.Pattern | str | None) -> re.Pattern | None:
    if isinstance(reg, str):
        return re.compile(reg)
    else:
        return reg


class DanmakuPHandlerSettings(blivedm.HandlerSettings):
    ignore_danmaku: re.Pattern | None = None
    validate_ignore_danmaku = pydantic.validator('ignore_danmaku', pre=True, allow_reuse=True)(try_compile)

    ignore_rate: float = 0.0
    dim_rate: float = 0.25

    @pydantic.validator('dim_rate')
    def ignore_less_than_dim(cls, v, values):
        if values['ignore_rate'] > v:
            raise ValueError('must contain a space')
        return v

    show_interact_word: bool = False

    test_flags: list[str] = []

    @pydantic.validator('test_flags', pre=True)
    def split_flags(cls, v):  # noqa
        if isinstance(v, str):
            v = v.split(',')
        return v

    ui: UI | None = None


class DanmakuPHandler(blivedm.BaseHandler[DanmakuPHandlerSettings]):
    @cached_property
    def ui(self):
        if self.settings.ui is None:
            raise ValueError('this handler do not use ui')
        return self.settings.ui

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

    def trivial_rate(self, info: blivedm.models.danmu_msg.DanmakuInfo) -> float:
        if self.settings.ignore_danmaku is not None and self.settings.ignore_danmaku.match(info.msg):
            return -1
        if info.mode_info.extra.emoticon_unique:  # 单一表情
            return 0.1
        orig_msg = msg = info.msg
        msg = self.kaomoji_regex.sub("", msg)
        orig_msg = self.kaomoji_regex.sub(".", orig_msg)
        msg = msg.replace("打卡", "")
        orig_msg = orig_msg.replace("打卡", ".")
        msg = msg.replace(".", "", 1)
        if info.mode_info.extra.emots is not None:
            for emot in info.mode_info.extra.emots.keys():
                msg = msg.replace(emot, "")
                orig_msg = orig_msg.replace(emot, "$")
        return len(msg) / len(orig_msg)

    async def on_danmu_msg(self, client, message: blivedm.DanmakuCommand):
        uname = message.info.uname
        msg = message.info.msg
        room_id = client.room_id
        trivial_rate = self.trivial_rate(message.info)

        # ==== testing: entropy ====
        if 'entropy' in self.settings.test_flags:
            tokens = []
            if message.info.mode_info.extra.emots is not None:
                self.kaomojis.update(message.info.mode_info.extra.emots.keys())
            for s in re.split('(' + '|'.join(re.escape(kaomoji) for kaomoji in self.kaomojis) + ')', msg):
                if s in self.kaomojis:
                    tokens.append(s)
                else:
                    tokens.extend(self.tokenizer.lcut(msg))
            entropy = self.entropy.calculate_and_add_tokens(tokens)
            if self.settings.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f": "),
                    PlainText(text=f"{tokens}"),
                    PlainText(
                        text=f" ({entropy=:.3f}, {entropy/len(tokens)=:.3f}, {trivial_rate=:.3f})"),
                ]))
            else:
                logger.info(
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): {escape(str(tokens))}"
                    f" ({entropy=:.3f}, {entropy/len(tokens)=:.3f}, {trivial_rate=:.3f})")
            return
        # ==== testing: entropy ====

        if trivial_rate < self.settings.ignore_rate:
            pass
        elif trivial_rate < self.settings.dim_rate:
            if self.settings.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f": "),
                    PlainText(text=msg),
                    PlainText(text=f" (trivial {trivial_rate})"),
                ]))
            else:
                logger.info(
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [grey]{escape(msg)}[/]")
        else:
            if self.settings.ui is not None:
                self.ui.add_record(Record(segments=[
                    ColorSeeSee(text=f"[{room_id}] "),
                    User(name=uname, uid=message.info.uid),
                    PlainText(text=f"说: "),
                    PlainText(text=msg),
                ]))
            else:
                logger.info(
                    rf"\[[bright_cyan]{room_id}[/]] {uname} (uid={message.info.uid}): [bright_white]{escape(msg)}[/]")

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id

        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"直播间信息变更"),
                RoomTitle(title=title, room_id=room_id),
                PlainText(text=f"，分区：{parent_area_name}/{area_name}"),
            ]))
        else:
            logger.info(
                rf"\[[bright_cyan]{room_id}[/]] "
                f"直播间信息变更《[rgb(255,212,50)]{escape(title)}[/]》，分区：{parent_area_name}/{area_name}")

    async def on_warning(self, client, message: blivedm.models.WarningCommand):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text=f"受到警告 {message.msg}"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [white on red]{message}[/]")

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=uname, uid=message.data.uid),
                PlainText(text=f"[¥{price}]: {msg}")
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] {uname} \[[bright_cyan]¥{price}[/]]: [{color}]{escape(msg)}[/]")

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="用户被封禁"),
                User(name=message.data.uname, uid=message.data.uid),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                        f"[red]用户 {message.data.uname}（uid={message.data.uid}）被封禁[/]")

    async def on_live(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播开始"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] "
                        "[black on #eeaaaa]:black_right__pointing_triangle_with_double_vertical_bar-text:直播开始[/]")

    async def on_preparing(self, client, message):
        room_id = client.room_id
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                PlainText(text="\N{Black Square For Stop}\N{VS16}直播结束"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] [black on #eeaaaa]:black_square_for_stop-text:直播结束[/]")

    async def on_interact_word(self, client, model):
        if not self.settings.show_interact_word:
            return
        room_id = client.room_id
        c = ["", "进入", "关注", "分享", "特别关注", "互相关注"]
        if self.settings.ui is not None:
            self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=model.data.uname, uid=model.data.uid),
                PlainText(text=c[model.data.msg_type]),
                PlainText(text="了直播间"),
            ]))
        else:
            logger.info(rf"\[[bright_cyan]{room_id}[/]] 用户 {model.data.uname}（uid={model.data.uid}）"
                        rf"{c[model.data.msg_type]}了直播间")
