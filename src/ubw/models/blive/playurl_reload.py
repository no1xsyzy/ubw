from ._base import *


class ReloadPlayurl(BaseModel):
    need: bool
    scatter: int
    qn: int


class ReloadOption(BaseModel):
    reload_stream_name: list[None]
    reload_format: list[None]
    scatter: int
    qn: int = 0
    fallback: bool = False
    reload_playurl: ReloadPlayurl | None = None


class DetailDesc(BaseModel):
    desc: str
    tag: list[str] | None = None


class BriefDesc(BaseModel):
    desc: str
    badge: str | None = None


class MediaBaseDesc(BaseModel):
    detail_desc: DetailDesc
    brief_desc: BriefDesc


class GQnDescItem(BaseModel):
    qn: int
    desc: str
    hdr_desc: str
    attr_desc: None
    hdr_type: int
    media_base_desc: MediaBaseDesc | None


class AudioCodecs(BaseModel):
    base: str | None = None


class VideoCodecs(BaseModel):
    base: str | None = None


class CodecItem(BaseModel):
    codec_name: str
    current_qn: int
    accept_qn: list[int]
    base_url: str
    url_info: list
    hdr_qn: None
    dolby_type: int
    attr_name: str
    hdr_type: int

    drm: bool = False

    drm_key_systems: None = None
    audio_codecs: AudioCodecs | None = None
    video_codecs: VideoCodecs | None = None


class FormatItem(BaseModel):
    format_name: str
    codec: list[CodecItem]
    master_url: str


class StreamItem(BaseModel):
    protocol_name: str
    format: list[FormatItem]


class P2pData(BaseModel):
    p2p: bool
    p2p_type: int
    m_p2p: bool
    m_servers: None


class Playurl(BaseModel):
    cid: int
    g_qn_desc: list[GQnDescItem]
    stream: list[StreamItem]
    p2p_data: P2pData
    dolby_qn: None


class Data(BaseModel):
    reload_option: ReloadOption
    playurl: Playurl
    room_id: int | None = None


class PlayurlReloadCommand(CommandModel):
    cmd: Literal['PLAYURL_RELOAD']
    data: Data
