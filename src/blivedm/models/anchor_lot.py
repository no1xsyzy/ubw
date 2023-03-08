from ._base import *


class DanmuNew(BaseModel):
    danmu: str
    danmu_view: str
    reject: bool


class AnchorLotStartData(BaseModel):
    asset_icon: str
    asset_icon_webp: str
    award_image: str
    award_name: str
    award_num: int
    award_type: int
    cur_gift_num: int
    current_time: datetime
    danmu: str
    danmu_new: list[DanmuNew]
    danmu_type: int
    gift_id: int
    gift_name: str
    gift_num: int
    gift_price: int
    goaway_time: str
    goods_id: int
    id: int
    is_broadcast: int
    join_type: int
    lot_status: int
    max_time: int
    require_text: str
    require_type: int
    require_value: int
    room_id: int
    send_gift_ensure: int
    show_panel: int
    start_dont_popup: int
    status: int
    time: int
    url: str
    web_url: str


class AnchorLotStartCommand(CommandModel):
    """天选时刻开始"""
    cmd: Literal['ANCHOR_LOT_START']
    data: AnchorLotStartData


class AwardUser(BaseModel):
    uid: int
    uname: str
    face: str
    level: int
    color: Color
    num: int


class AnchorLotAwardData(BaseModel):
    award_dont_popup: int
    award_image: str
    award_name: str
    award_num: int
    award_type: int
    award_users: list[AwardUser]
    id: int
    lot_status: int
    url: str
    web_url: str


class AnchorLotAwardCommand(CommandModel):
    """天选时刻中奖"""
    cmd: Literal['ANCHOR_LOT_AWARD']
    data: AnchorLotAwardData


class AnchorLotEndData(BaseModel):
    id: int


class AnchorLotEndCommand(CommandModel):
    """天选时刻结束"""
    cmd: Literal['ANCHOR_LOT_END']
    data: AnchorLotEndData


class AnchorLotCheckStatusData(BaseModel):
    id: int
    status: int
    uid: int
    """主播uid"""


class AnchorLotCheckStatusCommand(CommandModel):
    """天选时刻状态检查"""
    cmd: Literal['ANCHOR_LOT_CHECKSTATUS']
    data: AnchorLotCheckStatusData
