from __future__ import annotations

import re
import warnings
from datetime import datetime, timedelta
from functools import cached_property
from typing import *

from pydantic import BaseModel, field_validator, Field, AliasPath, TypeAdapter, AliasChoices, Json

__all__ = (
    'Response', 'OffsetList',
    'RoomInfo', 'InfoByRoom', 'DanmuInfo', 'RoomEmoticons', 'FingerSPI', 'RoomPlayInfo',
    'Dynamic', 'DynamicItem', 'AccountInfo',
    'Nav',
    'VideoP', 'VideoPlayInfo',
)

DataV = TypeVar('DataV')


class Response(BaseModel, Generic[DataV]):
    code: int
    message: str
    ttl: int = -1
    data: DataV | None = None


class OffsetList(BaseModel, Generic[DataV]):
    has_more: bool
    items: list[DataV]
    offset: str


class BaseInfo(BaseModel):
    uname: str
    face: str
    gender: str


class AnchorInfo(BaseModel):
    base_info: BaseInfo


class RoomInfo(BaseModel):
    """
    :var live_start_time: API result ``0`` is validated as ``None``, meaning not living
    """
    room_id: int
    short_id: int
    uid: int
    live_start_time: datetime | None
    title: str
    cover: str
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    keyframe: str
    """关键帧URL"""

    @field_validator('live_start_time', mode='before')
    def live_start_time_zero_means_none(cls, v):
        if v == 0:
            return None
        return v


class SilentRoomInfo(BaseModel):
    type: str
    level: int
    second: int
    expire_time: int


class InfoByRoom(BaseModel):
    room_info: RoomInfo
    silent_room_info: SilentRoomInfo
    anchor_info: AnchorInfo
    ct: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class Host(BaseModel):
    host: str
    port: int
    wss_port: int
    ws_port: int


class DanmuInfo(BaseModel):
    group: str
    business_id: int
    refresh_row_factor: float
    refresh_rate: int
    max_delay: int
    token: str
    host_list: list[Host]


class Emoticon(BaseModel):
    emoji: str
    descript: str
    url: str
    width: int
    height: int
    emoticon_unique: str
    emoticon_id: int

    identity: int
    """解锁需要99=无需求，4=粉丝团，3=舰长，2=提督，1=总督"""
    unlock_need_level: int
    """解锁需要粉丝牌等级"""
    unlock_show_text: int
    """解锁需求文字描述"""


class EmoticonPkg(BaseModel):
    emoticons: list[Emoticon]
    pkg_id: int
    pkg_name: str
    pkg_type: int
    pkg_descript: str
    current_cover: str


class RoomEmoticons(BaseModel):
    fans_brand: int
    data: list[EmoticonPkg]
    purchase_url: str | None = None


class FingerSPI(BaseModel):
    b_3: str
    b_4: str


class QnDesc(BaseModel):
    attr_desc: None
    desc: str
    hdr_desc: str
    qn: int


class P2PData(BaseModel):
    m_p2p: bool
    m_servers: list[str] | None
    p2p: bool
    p2p_type: int


class UrlInfo(BaseModel):
    extra: str
    host: str
    stream_ttl: int


class Codec(BaseModel):
    codec_name: str
    accept_qn: list[int]
    attr_name: str
    base_url: str
    current_qn: int
    dolby_type: int
    hdr_qn: None
    url_info: list[UrlInfo]


class Format(BaseModel):
    format_name: str
    codec: list[Codec]


class Stream(BaseModel):
    protocol_name: str
    format: list[Format]


class PlayUrl(BaseModel):
    cid: int
    dolby_qn: None
    g_qn_desc: list[QnDesc]
    p2p_data: P2PData
    stream: list[Stream]


class PlayUrlInfo(BaseModel):
    conf_json: str
    playurl: PlayUrl | None


class RoomPlayInfo(BaseModel):
    all_special_types: list[int]
    is_portrait: bool
    live_status: int
    live_time: datetime
    official_room_id: int
    official_type: int
    room_id: int
    short_id: int
    uid: int
    playurl_info: PlayUrlInfo | None


class LikeIcon(BaseModel):
    action_url: str
    end_url: str
    id: int
    start_url: str


class DynamicBasic(BaseModel):
    comment_id_str: str
    comment_type: int
    like_icon: LikeIcon
    rid_str: str
    jump_url: str = ""


class ModuleAuthor(BaseModel):
    mid: int
    name: str
    pub_ts: datetime


class RichTextNodeBase(BaseModel):
    type: str
    orig_text: str
    text: str


class RichTextNodeTypeText(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_TEXT']


class RichTextNodeTypeAt(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_AT']
    rid: int


class Emoji(BaseModel):
    icon_url: str


class RichTextNodeTypeEmoji(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_EMOJI']
    emoji: Emoji


class RichTextNodeTypeWeb(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_WEB']
    jump_url: str


class RichTextNodeTypeBv(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_BV']
    jump_url: str
    rid: str


class RichTextNodeTypeLottery(RichTextNodeBase):
    """可能是互动抽奖"""
    type: Literal['RICH_TEXT_NODE_TYPE_LOTTERY']
    rid: str


class Goods(BaseModel):
    jump_url: str
    type: int


class RichTextNodeTypeGoods(RichTextNodeBase):
    """可能是UP主的推荐"""
    type: Literal['RICH_TEXT_NODE_TYPE_GOODS']
    rid: str
    jump_url: str
    icon_name: str
    goods: Goods


class RichTextNodeTypeTopic(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_TOPIC']
    jump_url: str


class RichTextNodeTypeVote(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_VOTE']
    rid: str


RichTextNode = Annotated[
    Union[
        RichTextNodeTypeText, RichTextNodeTypeAt, RichTextNodeTypeEmoji, RichTextNodeTypeWeb, RichTextNodeTypeBv,
        RichTextNodeTypeLottery, RichTextNodeTypeGoods, RichTextNodeTypeTopic, RichTextNodeTypeVote,
    ],
    Field(discriminator='type')
]

TA_L_RTN = TypeAdapter(list[RichTextNode])


class RichText(BaseModel):
    rich_text_nodes: list[RichTextNode]
    text: str


class Pic(BaseModel):
    url: str


class Opus(BaseModel):
    jump_url: str
    summary: RichText
    pics: list[Pic]


class Archive(BaseModel):
    aid: str
    jump_url: str
    bvid: str

    cover: str
    title: str
    desc: str
    duration_text: str
    # duration_text: timedelta


class BaseMajor(BaseModel):
    type: str | None


class MajorOpus(BaseMajor):
    type: Literal['MAJOR_TYPE_OPUS']
    opus: Opus


class MajorArchive(BaseMajor):
    type: Literal['MAJOR_TYPE_ARCHIVE']
    archive: Archive


class LivePlayInfo(BaseModel):
    title: str
    room_id: int
    live_start_time: datetime


class LiveRcmdContent(BaseModel):
    live_play_info: LivePlayInfo


class LiveRcmd(BaseModel):
    content: Json[LiveRcmdContent] | LiveRcmdContent


class MajorLiveRcmd(BaseMajor):
    type: Literal['MAJOR_TYPE_LIVE_RCMD']
    live_rcmd: LiveRcmd


class Draw(BaseModel):
    id: int


class MajorDraw(BaseMajor):
    type: Literal['MAJOR_TYPE_DRAW']
    draw: Draw


class MajorNull(BaseMajor):
    type: Literal[None]


class Common(BaseModel):
    jump_url: str


class MajorCommon(BaseMajor):
    type: Literal['MAJOR_TYPE_COMMON']
    common: Common


class MajorNoneInfo(BaseModel):
    tips: str


class MajorNone(BaseMajor):
    type: Literal['MAJOR_TYPE_NONE']
    none: MajorNoneInfo


Major = Annotated[Union[
    MajorOpus, MajorArchive, MajorLiveRcmd, MajorDraw, MajorNull, MajorCommon, MajorNone,
], Field(discriminator='type')]


class ModuleDynamic(BaseModel):
    major: Major | None = None
    desc: RichText | None = None


class ModuleTag(BaseModel):
    text: str


class ModuleCollection(BaseModel):
    module_dynamic: ModuleDynamic | None = None
    module_author: ModuleAuthor | None = None
    module_tag: ModuleTag | None = None


def markdown_escape(x):
    x = re.sub(r'([\\\[\](){}#+\-.!|*_`])', r'\\\1', x)
    x = x.replace("\n", "\n\n")
    x = re.sub(r'\n{2,}', r'\n\n', x)
    return x


class DynamicItem(BaseModel):
    """
    :var type: 可能的值：
    DYNAMIC_TYPE_ARTICLE=文章、笔记
    DYNAMIC_TYPE_AV=视频
    DYNAMIC_TYPE_COMMON_SQUARE=带链接
    DYNAMIC_TYPE_DRAW=带图片
    DYNAMIC_TYPE_FORWARD=转发
    DYNAMIC_TYPE_WORD=纯文字
    """
    basic: DynamicBasic
    id_str: str | None
    modules: ModuleCollection
    type: str
    visible: bool
    orig: DynamicItem | None = None

    @property
    def is_forward(self):
        return self.type == 'DYNAMIC_TYPE_FORWARD'

    @property
    def is_video(self):
        return self.type == 'DYNAMIC_TYPE_AV'

    @property
    def is_live(self):
        return self.type == 'DYNAMIC_TYPE_LIVE_RCMD'

    @property
    def is_article(self):
        return self.type == 'DYNAMIC_TYPE_ARTICLE'

    @property
    def archive(self):
        return

    @property
    def major_type(self):
        try:
            major = self.modules.module_dynamic.major
            if major is None:
                return None
            return major.type
        except KeyError as e:
            warnings.warn(f"err in major_type {e=} {self.id_str=}")
            return None

    @cached_property
    def rich_text_nodes(self) -> list[RichTextNode]:
        match self.modules.module_dynamic.major:
            case MajorNull() | MajorDraw() | MajorCommon():
                return self.modules.module_dynamic.desc.rich_text_nodes
            case MajorOpus(opus=opus):
                opus: Opus
                return opus.summary.rich_text_nodes
            case None:
                if self.type == 'DYNAMIC_TYPE_FORWARD':
                    return self.modules.module_dynamic.desc.rich_text_nodes
        return []

    @cached_property
    def markdown(self) -> str:
        s = ""
        for n in self.rich_text_nodes:
            match n:
                case RichTextNodeTypeAt(text=text, rid=rid):
                    s = f"{s}[{markdown_escape(text)}](https://space.bilibili.com/{rid})"
                case RichTextNodeTypeEmoji(emoji=Emoji(icon_url=icon_url), text=text):
                    s = f"{s}![{markdown_escape(text)}]({icon_url})"
                case RichTextNodeTypeWeb(text=text, jump_url=jump_url):
                    s = f"{s}[{markdown_escape(text)}]({jump_url})"
                case RichTextNodeTypeText(text=text):
                    s = f"{s}{markdown_escape(text)}"
                case RichTextNodeTypeBv(text=text, rid=rid):
                    s = f"{s}[{markdown_escape(text)}](https://www.bilibili.com/video/{rid})"
                case RichTextNodeTypeLottery(text=text):
                    s = f"{s}{markdown_escape(text)}"
                case RichTextNodeTypeGoods(text=text, jump_url=jump_url):
                    s = f"{s}[{markdown_escape(text)}]({jump_url})"
                case RichTextNodeTypeVote(text=text):
                    s = f"{s}[投票：{markdown_escape(text)}]"
        return s

    @cached_property
    def text(self) -> str:
        match self.modules.module_dynamic.major:
            case MajorNull() | MajorDraw() | MajorCommon():
                return self.modules.module_dynamic.desc.text
            case MajorOpus(opus=opus):
                opus: Opus
                return opus.summary.text
            case MajorLiveRcmd(live_rcmd=live_rcmd):
                live_rcmd: LiveRcmd
                return live_rcmd.content.live_play_info.title
            case MajorArchive(archive=archive):
                return archive.title + '\n\n' + archive.desc
            case None:
                if self.type == 'DYNAMIC_TYPE_FORWARD':
                    return self.modules.module_dynamic.desc.text
        return ''

    @cached_property
    def jump_url(self) -> str:
        match self.modules.module_dynamic.major:
            case MajorCommon(common=common):
                common: Common
                return common.jump_url
            case MajorOpus(opus=opus):
                opus: Opus
                return "https:" + opus.jump_url
            case MajorLiveRcmd(live_rcmd=live_rcmd):
                live_rcmd: LiveRcmd
                return f"https://live.bilibili.com/{live_rcmd.content.live_play_info.room_id}"
            case MajorArchive(archive=archive):
                return "https:" + archive.jump_url
        return f"https://t.bilibili.com/{self.id_str}"

    @cached_property
    def pictures(self) -> list[str]:
        match self.modules.module_dynamic.major:
            case MajorOpus(opus=opus):
                opus: Opus
                return [pic.url for pic in opus.pics]
        return []

    @cached_property
    def pub_date(self):
        match self.modules.module_author:
            case ModuleAuthor(pub_ts=pubtime):
                return pubtime
            case _:
                return datetime.now()

    @cached_property
    def is_topped(self):
        if self.modules.module_tag is not None:
            return self.modules.module_tag.text == '置顶'
        return False


class Dynamic(BaseModel):
    item: DynamicItem


class AccountInfo(BaseModel):
    mid: int
    live_room_id: int = Field(
        alias='live_room_id',
        validation_alias=AliasChoices('live_room_id',
                                      AliasPath('live_room', 'roomid')))


class Nav(BaseModel):
    wbi_img_url: str = Field(
        alias='wbi_img_url',
        validation_alias=AliasChoices('wbi_img_url',
                                      AliasPath('wbi_img', 'img_url')))
    wbi_img_sub_url: str = Field(
        alias='wbi_img_sub_url',
        validation_alias=AliasChoices('wbi_img_sub_url',
                                      AliasPath('wbi_img', 'sub_url')))


class VideoP(BaseModel):
    """
    视频分P
    :var cid: 分P编号
    :var page: 第几分P
    """
    cid: int
    page: int


class SegmentBase(BaseModel):
    initialization: str
    index_range: str


class DashAV(BaseModel):
    id: int
    base_url: Annotated[str, Field(validation_alias=AliasChoices('baseUrl', 'base_url', 'url'))]
    backup_url: Annotated[list[str], Field(validation_alias=AliasChoices('backupUrl', 'backup_url'))]
    segment_base: Annotated[SegmentBase, Field(validation_alias=AliasChoices('segment_base', 'SegmentBase'))]
    codecs: str
    width: int
    height: int
    mime_type: str
    bandwidth: float

    @property
    def apparent_fid(self):
        return re.search(r'-(\d+).m4s', self.base_url)[1]


class Dash(BaseModel):
    duration: timedelta
    video: list[DashAV]
    audio: list[DashAV]


class VideoPlayInfo(BaseModel):
    dash: Dash
