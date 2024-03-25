import json
import warnings
from datetime import datetime, timezone, timedelta
from functools import cached_property
from typing import *

from pydantic import BaseModel, field_validator, Field, AliasPath, TypeAdapter

__all__ = (
    'Response', 'OffsetList',
    'RoomInfo', 'InfoByRoom', 'DanmuInfo', 'RoomEmoticons', 'FingerSPI', 'RoomPlayInfo',
    'Dynamic', 'DynamicItem', 'AccountInfo',
    'Nav',
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
    ct: datetime = Field(default_factory=lambda: datetime.now(timezone(timedelta(seconds=8 * 3600))))


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
    playurl: PlayUrl


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


class RichTextNodeTypeEmoji(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_EMOJI']


RichTextNode = Annotated[
    Union[RichTextNodeTypeText, RichTextNodeTypeAt, RichTextNodeTypeEmoji],
    Field(discriminator='type')
]

TA_L_RTN = TypeAdapter(list[RichTextNode])


class DynamicItem(BaseModel):
    basic: DynamicBasic
    id_str: str
    modules: dict
    type: str
    visible: bool

    @cached_property
    def major_type(self):
        try:
            major = self.modules['module_dynamic']['major']
            if major is None:
                return None
            return major['type']
        except KeyError as e:
            warnings.warn(f"err in major_type {e=} {self.id_str=}")
            return None

    @cached_property
    def live_rcmd(self):
        try:
            return json.loads(self.modules['module_dynamic']['major']['live_rcmd']['content'])
        except KeyError as e:
            warnings.warn(f"err in live_rcmd {e=} {self.id_str=}")
            return {}

    @cached_property
    def rich_text_nodes(self) -> list[RichTextNode]:
        try:
            major_type = self.major_type
            if major_type is None or major_type == 'MAJOR_TYPE_DRAW':
                return TA_L_RTN.validate_python(self.modules['module_dynamic']['desc']['rich_text_nodes'])
            elif major_type == 'MAJOR_TYPE_OPUS':
                return TA_L_RTN.validate_python(
                    self.modules['module_dynamic']['major']['opus']['summary']['rich_text_nodes'])
        except KeyError as e:
            warnings.warn(f"err in rich_text_nodes {e=} {self.id_str=}")
        return []

    @cached_property
    def text(self) -> str:
        try:
            major_type = self.major_type
            if major_type is None or major_type == 'MAJOR_TYPE_DRAW':
                return self.modules['module_dynamic']['desc']['text']
            elif major_type == 'MAJOR_TYPE_OPUS':
                return self.modules['module_dynamic']['major']['opus']['summary']['text']
            elif major_type == 'MAJOR_TYPE_LIVE_RCMD':
                return self.live_rcmd['live_play_info']['title']
            elif major_type == 'MAJOR_TYPE_ARCHIVE':
                return self.modules['module_dynamic']['major']['archive']['title']
        except KeyError as e:
            warnings.warn(f"err in text {e=} {self.id_str=}")
        return ""

    @cached_property
    def jump_url(self) -> str:
        try:
            major_type = self.major_type
            if major_type == 'MAJOR_TYPE_OPUS':
                return "https:" + self.modules['module_dynamic']['major']['opus']['jump_url']
            elif major_type == 'MAJOR_TYPE_LIVE_RCMD':
                return f"https://live.bilibili.com/blanc/{self.live_rcmd['live_play_info']['room_id']}"
            elif major_type == 'MAJOR_TYPE_ARCHIVE':
                return "https:" + self.modules['module_dynamic']['major']['archive']['jump_url']
        except KeyError as e:
            warnings.warn(f"err in jump_url {e=} {self.id_str=}")
        return f"https://t.bilibili.com/{self.id_str}"

    @cached_property
    def pub_date(self):
        try:
            return datetime.fromtimestamp(self.modules['module_author']['pub_ts'])
        except KeyError as e:
            warnings.warn(f"err in pub_date {e=} {self.id_str=}")
            return datetime.now()

    @cached_property
    def is_topped(self):
        try:
            return 'module_tag' in self.modules and self.modules['module_tag']['text'] == '置顶'
        except KeyError as e:
            warnings.warn(f"err in is_topped {e=} {self.id_str=}")
            return False


class Dynamic(BaseModel):
    item: DynamicItem


class AccountInfo(BaseModel):
    mid: int
    live_room_id: int = Field(alias='live_room_id',
                              validation_alias=AliasPath('live_room', 'roomid'))


class Nav(BaseModel):
    wbi_img_url: str = Field(alias='wbi_img_url',
                             validation_alias=AliasPath('wbi_img', 'img_url'))
    wbi_img_sub_url: str = Field(alias='wbi_img_sub_url',
                                 validation_alias=AliasPath('wbi_img', 'sub_url'))
