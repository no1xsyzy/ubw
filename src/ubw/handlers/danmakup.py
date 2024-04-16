import functools
import re
from datetime import timezone, timedelta
from functools import cached_property

from pydantic import field_validator, model_validator

from ubw.ui import Record, PlainText, User, RoomTitle, UI, ColorSeeSee, Currency, Richy
from ._base import *

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


def colorseesee(palette):
    @functools.lru_cache()
    def color_pair(text: str):
        return palette[hash(text) % len(palette)], palette[(hash(text) + len(text)) % len(palette)]

    def colored(text: str, color_override: str | int | None = None):
        color_def = str(color_override) if color_override is not None else text
        fg, bg = color_pair(color_def)
        return f"[{fg}][on {bg}]{escape(text[:1])}[/]{escape(text[1:])}[/]"

    return colored


css = colorseesee(('red', 'green', 'yellow', 'blue', 'magenta', 'cyan'))


class DanmakuPHandler(BaseHandler):
    cls: Literal['danmakup'] = 'danmakup'
    ignore_danmaku: re.Pattern | None = None

    ignore_rate: float = 0.0
    dim_rate: float = 0.25

    gift_threshold: float = 0.0

    show_interact_word: bool = False
    test_flags: list[str] = []

    ui: UI = Richy()
    owned_ui: bool = True

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
    def tokenizer(self):
        import jieba
        tok = jieba.Tokenizer()
        for kmj in KAOMOJIS:
            tok.add_word(kmj, tag='e')
            tok.suggest_freq(kmj, True)
        return tok

    def trivial_rate(self, info: models.blive.danmu_msg.DanmakuInfo) -> float:
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

    async def start(self, client):
        if self.owned_ui and self.ui is not None:
            await self.ui.start()

    async def on_danmu_msg(self, client, message: models.DanmakuCommand):
        uname = message.info.uname
        msg = message.info.msg
        uid = message.info.uid
        room_id = client.room_id
        face = message.info.mode_info.user.base.face
        trivial_rate = self.trivial_rate(message.info)

        if trivial_rate < self.ignore_rate:
            pass
        elif trivial_rate < self.dim_rate:
            await self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=uname, uid=uid, face=face),
                PlainText(text=f": "),
                PlainText(text=msg),
            ], time=message.ct))

        else:
            await self.ui.add_record(Record(segments=[
                ColorSeeSee(text=f"[{room_id}] "),
                User(name=uname, uid=uid, face=face),
                PlainText(text=f"说: "),
                PlainText(text=msg),
            ], time=message.ct))

    async def on_room_change(self, client, message):
        title = message.data.title
        parent_area_name = message.data.parent_area_name
        area_name = message.data.area_name
        room_id = client.room_id

        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text=f"直播间信息变更"),
            RoomTitle(title=title, room_id=room_id),
            PlainText(text=f"，分区：{parent_area_name}/{area_name}"),
        ], time=message.ct))

    async def on_summary(self, client, summary):
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text=summary.msg),
            Currency(price=summary.price),
            PlainText(text=f" ({summary.raw.cmd})"),
        ], time=summary.t.astimezone(timezone(timedelta(seconds=8 * 3600)))))

    async def on_warning(self, client, message: models.WarningCommand):
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text=f"受到警告 {message.msg}"),
        ], time=message.ct))

    async def on_super_chat_message(self, client, message):
        uname = message.data.user_info.uname
        uid = message.data.uid
        price = message.data.price
        msg = message.data.message
        color = message.data.message_font_color
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            User(name=uname, uid=uid, face=message.data.user_info.face),
            PlainText(text=f"[¥{price}]: {msg}")
        ], time=message.ct))

    async def on_room_block_msg(self, client, message):
        room_id = client.room_id
        uid = message.data.uid
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text="用户被封禁"),
            User(name=message.data.uname, uid=uid),
        ], time=message.ct))

    async def on_live(self, client, message):
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text="\N{Black Right-Pointing Triangle With Double Vertical Bar}\N{VS16}直播开始"),
        ], time=message.ct))

    async def on_preparing(self, client, message):
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            PlainText(text="\N{Black Square For Stop}\N{VS16}直播结束"),
        ], time=message.ct))

    async def on_interact_word(self, client, model):
        if not self.show_interact_word:
            return
        uid = model.data.uid
        room_id = client.room_id
        await self.ui.add_record(Record(segments=[
            ColorSeeSee(text=f"[{room_id}] "),
            User(name=model.data.uname, uid=uid, face=model.data.uinfo.base.face),
            PlainText(text=model.MSG_NAME[model.data.msg_type]),
            PlainText(text="了直播间"),
        ], time=model.ct))

    async def on_x_ubw_heartbeat(self, client, message):
        pass

    async def on_send_gift(self, client, model: models.GiftCommand):
        room_id = client.room_id
        uid = model.data.uid
        money = model.data.price * model.data.num / 1000
        uname = model.data.uname

        if money < self.gift_threshold:
            return

        segments = [
            ColorSeeSee(text=f"[{room_id}] "),
            User(name=uname, uid=uid, face=model.data.face),
            PlainText(text=f"{model.data.action}了 {model.data.giftName}x{model.data.num}"),
        ]
        if model.data.coin_type == 'gold':
            segments.append(Currency(price=money))
        await self.ui.add_record(Record(segments=segments, time=model.ct))
