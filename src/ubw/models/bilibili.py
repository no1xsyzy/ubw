from datetime import datetime, timezone, timedelta
from typing import *

from pydantic import BaseModel, field_validator, Field, AliasPath, AliasChoices

__all__ = (
    'Response', 'InfoByRoom', 'DanmuInfo', 'RoomEmoticons', 'FingerSPI', 'RoomPlayInfo', 'Dynamic', 'AccountInfo',
    'Nav',
)

DataV = TypeVar('DataV')


class Response(BaseModel, Generic[DataV]):
    code: int
    message: str
    ttl: int = -1
    data: DataV | None = None


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


class ModuleAuthor(BaseModel):
    mid: int
    name: str


class RichTextNodeBase(BaseModel):
    type: str
    orig_text: str
    text: str


class RichTextNodeTypeText(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_TEXT']


class RichTextNodeTypeAt(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_AT']
    rid: int


RichTextNode = Annotated[
    Union[RichTextNodeTypeText, RichTextNodeTypeAt],
    Field(discriminator='type')
]


class ModuleDynamic(BaseModel):
    rich_text_nodes: list[RichTextNode] = Field(
        alias='rich_text_nodes',
        validation_alias=AliasChoices(
            AliasPath('major', 'opus', 'summary', 'rich_text_nodes'),
            AliasPath('desc', 'rich_text_nodes'),
        ),
    )
    text: str = Field(
        alias='text',
        validation_alias=AliasChoices(
            AliasPath('major', 'opus', 'summary', 'text'),
            AliasPath('desc', 'text'),
        ),
    )


class DynamicItem(BaseModel):
    basic: DynamicBasic
    id_str: str
    module_author: ModuleAuthor = Field(alias='module_author',
                                        validation_alias=AliasPath('modules', 'module_author'))
    module_dynamic: ModuleDynamic = Field(alias='module_dynamic',
                                          validation_alias=AliasPath('modules', 'module_dynamic'))
    type: str
    visible: bool


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
