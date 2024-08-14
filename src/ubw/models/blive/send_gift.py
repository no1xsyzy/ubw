from ._base import *


class BlindGift(BaseModel):
    blind_gift_config_id: int
    from_: int = Field(alias='from')
    gift_action: str
    gift_tip_price: int
    original_gift_id: int
    original_gift_name: str
    original_gift_price: int


class BatchComboSend(BaseModel):
    action: str
    batch_combo_id: str
    batch_combo_num: int
    blind_gift: BlindGift | None = None
    gift_id: int
    gift_name: str
    gift_num: int
    send_master: None = None
    uid: int
    uname: str


class ComboSend(BaseModel):
    action: str
    combo_id: str
    combo_num: int
    gift_id: int
    gift_name: str
    gift_num: int
    send_master: None = None
    uid: int
    uname: str


class BagGift(BaseModel):
    price_for_show: int
    show_price: int  # maybe actually bool


class FaceEffectV2(BaseModel):
    id: int
    type: int


class GiftInfo(BaseModel):
    effect_id: int
    has_imaged_gift: int
    img_basic: str
    webp: str


class GiftData(BaseModel):
    """礼物消息
    :var giftName: 礼物名
    :var num: 数量
    :var uname: 用户名
    :var face: 用户头像URL
    :var guard_level: 舰队等级，0非舰队，1总督，2提督，3舰长
    :var uid: 用户ID
    :var timestamp: 时间戳
    :var giftId: 礼物ID
    :var giftType: 礼物类型（未知）
    :var action: 目前遇到的有'喂食'、'赠送'
    :var price: 礼物单价瓜子数
    :var rnd: 随机数，可能是去重用的。有时是时间戳+去重ID，有时是UUID
    :var coin_type: 瓜子类型，'silver'或'gold'，1000金瓜子 = 1元
    :var total_coin: 总瓜子数
    :var tid: 可能是事务ID，有时和rnd相同"""
    giftName: str
    num: int
    uname: str
    face: str
    guard_level: int
    uid: int
    timestamp: datetime
    giftId: int
    giftType: int
    action: str
    price: int
    rnd: str
    coin_type: str
    total_coin: int
    tid: str
    bag_gift: BagGift | None = None
    batch_combo_id: str = ''
    batch_combo_send: BatchComboSend | None = None
    beatId: str = '0'
    biz_source: str
    blind_gift: BlindGift | None = None
    broadcast_id: int = 0
    combo_resources_id: int = 1
    combo_send: ComboSend | None = None
    combo_stay_time: int = 5
    combo_total_coin: int = 0
    crit_prob: int = 0
    demarcation: int = 1
    discount_price: int = 0
    dmscore: int
    draw: int = 0
    effect: int = 0
    effect_block: int = 1
    face_effect_id: int = 0
    face_effect_type: int = 0
    float_sc_resource_id: float = 0
    gift_tag: list[int] = []
    group_medal: GroupMedal | None = None
    is_first: bool = False
    is_join_receiver: bool = False
    is_naming: bool = False
    is_special_batch: int = 0  # maybe bool
    magnification: float = 1
    medal_info: MedalInfo
    name_color: str = ''
    original_gift_name: str = ''
    rcost: int
    receive_user_info: UserInfo
    receiver_uinfo: Uinfo
    remain: int = 0
    send_master: None = None
    sender_uinfo: Uinfo

    gold: int = 0
    silver: int = 0

    super: int = 0
    super_batch_gift_num: int = 0
    super_gift_num: int = 0
    svga_block: int = 0
    switch: bool = True
    tag_image: str = ''
    top_list: None = None
    wealth_level: int = 0

    # 2024年7月24日更新
    face_effect_v2: FaceEffectV2 | None = None

    gift_info: GiftInfo | None = None


class GiftCommand(CommandModel):
    cmd: Literal['SEND_GIFT']
    data: GiftData

    def summarize(self) -> Summary:
        return Summary(
            t=self.data.timestamp,
            msg=f"{self.data.uname} {self.data.action}了 {self.data.giftName}x{self.data.num}",
            user=(self.data.uid, self.data.uname),
            price=self.data.price * self.data.num / 1000 if self.data.coin_type == 'gold' else 0,
            raw=self,
        )
