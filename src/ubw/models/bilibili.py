from __future__ import annotations

import re
from datetime import datetime, timedelta
from functools import cached_property
from typing import *

from pydantic import BaseModel, Field, AliasPath, TypeAdapter, AliasChoices, Json, BeforeValidator, RootModel

__all__ = (
    'Response', 'ResponseF', 'OffsetList',
    'RoomInfo', 'InfoByRoom', 'DanmuInfo', 'RoomEmoticons', 'FingerSPI', 'RoomPlayInfo',
    'Dynamic', 'DynamicItem', 'AccountInfo',
    'Nav',
    'VideoP', 'VideoPlayInfo',
)

DataV = TypeVar('DataV')
DataF = TypeVar('DataF')


class Response(BaseModel, Generic[DataV]):
    code: int
    message: str
    ttl: int = -1
    data: DataV | None = None


class ResponseF(BaseModel, Generic[DataV, DataF]):
    code: int
    message: str
    ttl: int = -1
    data: DataV | DataF


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
    live_start_time: Annotated[datetime | None, BeforeValidator(lambda v: None if v == 0 else v)]
    title: str
    cover: str
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    keyframe: str
    """关键帧URL"""


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

    class PlayUrlInfo(BaseModel):
        conf_json: Json[Conf]
        playurl: PlayUrl | None

        class Conf(BaseModel):
            cdn_rate: int
            report_interval_sec: int

        class PlayUrl(BaseModel):
            cid: int
            dolby_qn: None
            g_qn_desc: list[QnDesc]
            p2p_data: P2PData
            stream: list[Stream]

            class QnDesc(BaseModel):
                attr_desc: None
                desc: str
                hdr_desc: str
                qn: int
                hdr_type: int
                media_base_desc: MediaBaseDesc | None

                class MediaBaseDesc(BaseModel):
                    detail_desc: DetailDesc
                    brief_desc: BriefDesc

                    class DetailDesc(BaseModel):
                        desc: str
                        tag: list[str]

                    class BriefDesc(BaseModel):
                        desc: str
                        badge: str

            class P2PData(BaseModel):
                m_p2p: bool
                m_servers: list[str] | None
                p2p: bool
                p2p_type: int

            class Stream(BaseModel):
                protocol_name: str
                format: list[Format]

                class Format(BaseModel):
                    format_name: str
                    codec: list[Codec]

                    class Codec(BaseModel):
                        codec_name: str
                        accept_qn: list[int]
                        attr_name: str
                        base_url: str
                        current_qn: int
                        dolby_type: int
                        hdr_qn: None
                        url_info: list[UrlInfo]

                        class UrlInfo(BaseModel):
                            extra: str
                            host: str
                            stream_ttl: int


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
    emoji: Emoji

    class Emoji(BaseModel):
        icon_url: str


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


class RichTextNodeTypeGoods(RichTextNodeBase):
    """可能是UP主的推荐"""
    type: Literal['RICH_TEXT_NODE_TYPE_GOODS']
    rid: str
    jump_url: str
    icon_name: str
    goods: Goods

    class Goods(BaseModel):
        jump_url: str
        type: int


class RichTextNodeTypeTopic(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_TOPIC']
    jump_url: str


class RichTextNodeTypeVote(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_VOTE']
    rid: str


class RichTextNodeTypeAv(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_AV']


class RichTextNodeTypeCv(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_CV']


class RichTextNodeTypeMail(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_MAIL']


class RichTextNodeTypeNone(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_NONE']


class RichTextNodeTypeOgvEp(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_OGV_EP']


class RichTextNodeTypeOgvSeason(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_OGV_SEASON']


class RichTextNodeTypeTaobao(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_TAOBAO']


class RichTextNodeTypeViewPicture(RichTextNodeBase):
    type: Literal['RICH_TEXT_NODE_TYPE_VIEW_PICTURE']


RichTextNode = Annotated[
    Union[
        RichTextNodeTypeText, RichTextNodeTypeAt, RichTextNodeTypeEmoji, RichTextNodeTypeWeb, RichTextNodeTypeBv,
        RichTextNodeTypeLottery, RichTextNodeTypeGoods, RichTextNodeTypeTopic, RichTextNodeTypeVote,
        RichTextNodeTypeAv,
        RichTextNodeTypeCv,
        RichTextNodeTypeMail,
        RichTextNodeTypeNone,
        RichTextNodeTypeOgvEp,
        RichTextNodeTypeOgvSeason,
        RichTextNodeTypeTaobao,
        RichTextNodeTypeViewPicture,
    ],
    Field(discriminator='type')
]

TA_L_RTN = TypeAdapter(list[RichTextNode])


class RichText(BaseModel):
    rich_text_nodes: list[RichTextNode]
    text: str


class Major(RootModel):
    root: Annotated[Union[*(BaseMajor.__subclasses__()),], Field(discriminator='type')]

    class BaseMajor(BaseModel):
        type: str | None

    class Opus(BaseMajor):
        type: Literal['MAJOR_TYPE_OPUS']
        opus: Info

        class Info(BaseModel):
            jump_url: str
            summary: RichText
            pics: list[Pic]

            class Pic(BaseModel):
                url: str

    class Archive(BaseMajor):
        type: Literal['MAJOR_TYPE_ARCHIVE']
        archive: Info

        class Info(BaseModel):
            aid: str
            jump_url: str
            bvid: str

            cover: str
            title: str
            desc: str
            duration_text: str
            # duration_text: timedelta

    class LiveRcmd(BaseMajor):
        type: Literal['MAJOR_TYPE_LIVE_RCMD']
        live_rcmd: Info

        class Info(BaseModel):
            content: Json[Content] | Content

            class Content(BaseModel):
                live_play_info: LivePlayInfo

                class LivePlayInfo(BaseModel):
                    title: str
                    room_id: int
                    live_start_time: datetime

    class Draw(BaseMajor):
        type: Literal['MAJOR_TYPE_DRAW']
        draw: Info

        class Info(BaseModel):
            id: int

    class Null(BaseMajor):
        type: Literal[None]

    class Common(BaseMajor):
        type: Literal['MAJOR_TYPE_COMMON']
        common: Info

        class Info(BaseModel):
            jump_url: str

    class NoneM(BaseMajor):
        type: Literal['MAJOR_TYPE_NONE']
        none: Info

        class Info(BaseModel):
            tips: str

    class Applet(BaseMajor):
        type: Literal['MAJOR_TYPE_APPLET']

    class Article(BaseMajor):
        type: Literal['MAJOR_TYPE_ARTICLE']

    class Blocked(BaseMajor):
        type: Literal['MAJOR_TYPE_BLOCKED']

    class Courses(BaseMajor):
        type: Literal['MAJOR_TYPE_COURSES']

    class CourBatch(BaseMajor):
        type: Literal['MAJOR_TYPE_COUR_BATCH']

    class Live(BaseMajor):
        type: Literal['MAJOR_TYPE_LIVE']

    class Medialist(BaseMajor):
        type: Literal['MAJOR_TYPE_MEDIALIST']

    class Music(BaseMajor):
        type: Literal['MAJOR_TYPE_MUSIC']

    class Pgc(BaseMajor):
        type: Literal['MAJOR_TYPE_PGC']

    class Subscription(BaseMajor):
        type: Literal['MAJOR_TYPE_SUBSCRIPTION']

    class SubscriptionNew(BaseMajor):
        type: Literal['MAJOR_TYPE_SUBSCRIPTION_NEW']

    class UgcSeason(BaseMajor):
        type: Literal['MAJOR_TYPE_UGC_SEASON']

    class UpowerCommon(BaseMajor):
        type: Literal['MAJOR_TYPE_UPOWER_COMMON']


class Additional(RootModel):
    root: Annotated[Union[*(BaseAdditional.__subclasses__())], Field(discriminator='type')]

    class BaseAdditional(BaseModel):
        type: str

    class Reserve(BaseAdditional):
        """视频预约"""
        type: Literal['ADDITIONAL_TYPE_RESERVE']
        reserve: ReserveData

        class ReserveData(BaseModel):
            jump_url: str
            title: str

    class Goods(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_GOODS']
        goods: GoodsData

        class GoodsData(BaseModel):
            items: list[GoodsItem]

            class GoodsItem(BaseModel):
                cover: str
                id: int
                jump_url: str
                name: str

    class Common(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_COMMON']

    class Vote(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_VOTE']

    class Match(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_MATCH']

    class Ugc(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_UGC']

    class UpowerLottery(BaseAdditional):
        type: Literal['ADDITIONAL_TYPE_UPOWER_LOTTERY']


class Module(BaseModel):
    module_author: Author | None = None
    module_dynamic: Dynamic | None = None
    module_tag: Tag | None = None

    class Author(BaseModel):
        mid: int
        name: str
        pub_ts: datetime

    class Dynamic(BaseModel):
        major: Major | None = None
        desc: RichText | None = None
        additional: Additional | None = None

    class Tag(BaseModel):
        text: str


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
    modules: Module
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
        return self.modules.module_dynamic.major and self.modules.module_dynamic.major.root.type

    @cached_property
    def rich_text_nodes(self) -> list[RichTextNode]:
        match self.modules.module_dynamic.major and self.modules.module_dynamic.major.root:
            case Major.Null() | Major.Draw() | Major.Common():
                return self.modules.module_dynamic.desc.rich_text_nodes
            case Major.Opus(opus=opus):
                opus: Major.Opus.Info
                return opus.summary.rich_text_nodes
            case Major.Archive(archive=archive):
                return [  # reconstruct
                    RichTextNodeTypeBv(type='RICH_TEXT_NODE_TYPE_BV', orig_text=archive.title, text=archive.title,
                                       jump_url="https:" + archive.jump_url, rid=archive.bvid),
                    RichTextNodeTypeText(type='RICH_TEXT_NODE_TYPE_TEXT', text="\n\n" + archive.desc,
                                         orig_text="\n\n" + archive.desc),
                ]
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
                case RichTextNodeTypeEmoji(emoji=RichTextNodeTypeEmoji.Emoji(icon_url=icon_url), text=text):
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
                case _:
                    assert_never(n)
        for p in self.pictures:
            s = f"{s}\n![]({p})"
        match self.modules.module_dynamic.additional:
            case Additional.Reserve(reserve=reserve):
                if reserve.jump_url:
                    s = f"{s}\n[{markdown_escape(reserve.title)}]({reserve.jump_url})"
                else:
                    s = f"{s}\n{markdown_escape(reserve.title)}"
        return s

    @cached_property
    def text(self) -> str:
        match self.modules.module_dynamic.major and self.modules.module_dynamic.major.root:
            case Major.Null() | Major.Draw() | Major.Common():
                return self.modules.module_dynamic.desc.text
            case Major.Opus(opus=opus):
                opus: Major.Opus.Info
                return opus.summary.text
            case Major.LiveRcmd(live_rcmd=live_rcmd):
                live_rcmd: Major.LiveRcmd.Info
                return live_rcmd.content.live_play_info.title
            case Major.Archive(archive=archive):
                return archive.title + '\n\n' + archive.desc
            case None:
                if self.type == 'DYNAMIC_TYPE_FORWARD':
                    return self.modules.module_dynamic.desc.text
        return ''

    @cached_property
    def jump_url(self) -> str:
        match self.modules.module_dynamic.major and self.modules.module_dynamic.major.root:
            case Major.Common(common=common):
                common: Major.Common.Info
                return common.jump_url
            case Major.Opus(opus=opus):
                opus: Major.Opus.Info
                return "https:" + opus.jump_url
            case Major.LiveRcmd(live_rcmd=live_rcmd):
                live_rcmd: Major.LiveRcmd.Info
                return f"https://live.bilibili.com/{live_rcmd.content.live_play_info.room_id}"
            case Major.Archive(archive=archive):
                return "https:" + archive.jump_url
        return f"https://t.bilibili.com/{self.id_str}"

    @cached_property
    def pictures(self) -> list[str]:
        match self.modules.module_dynamic.major and self.modules.module_dynamic.major.root:
            case Major.Opus(opus=opus):
                opus: Major.Opus.Info
                return [pic.url for pic in opus.pics]
            case Major.Archive(archive=archive):
                return [archive.cover]
        return []

    @cached_property
    def pub_date(self):
        match self.modules.module_author:
            case Module.Author(pub_ts=pubtime):
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
    name: str
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
