# -*- coding: utf-8 -*-

from ._base import *
from .activity_banner_change import ActivityBannerChangeCommand
from .activity_banner_change_v2 import ActivityBannerChangeV2Command
from .anchor_helper_danmu import AnchorHelperDanmuCommand
from .anchor_lot import AnchorLotStartCommand, AnchorLotCheckStatusCommand, AnchorLotEndCommand, AnchorLotAwardCommand
from .area_rank_changed import AreaRankChangedCommand
from .card_msg import CardMsgCommand
from .combo_end import ComboEndCommand
from .combo_send import ComboSendCommand
from .common_notice_danmaku import CommonNoticeDanmakuCommand
from .cut_off import CutOffCommand
from .danmu_aggregation import DanmuAggregationCommand
from .danmu_msg import DanmakuCommand
from .entry_effect import EntryEffectCommand, EntryEffectMustReceiveCommand
from .full_screen_special_effect import FullScreenSpecialEffectCommand
from .gift_star_process import GiftStarProcessCommand
from .goto_buy_flow import GotoBuyFlowCommand
from .guard_buy import GuardBuyCommand
from .guard_honor_thousand import GuardHonorThousandCommand
from .heartbeat import HeartbeatCommand
from .hot_buy_num import HotBuyNumCommand
from .hot_rank_settlement import HotRankSettlementCommand, HotRankSettlementV2Command
from .hot_room_notify import HotRoomNotifyCommand
from .interact_word import InteractWordCommand
from .like_info import LikeInfoV3UpdateCommand, LikeInfoV3ClickCommand, LikeInfoV3NoticeCommand
from .live import LiveCommand
from .live_multi_view_change import LiveMultiViewChangeCommand
from .live_panel_change import LivePanelChangeCommand
from .log_in_notice import LogInNoticeCommand
from .messagebox_user_gain_medal import MessageboxUserGainMedalCommand
from .messagebox_user_medal_change import MessageboxUserMedalChangeCommand
from .notice_msg import NoticeMsgCommand
from .online_rank_count import OnlineRankCountCommand
from .pk import (
    PkBattleRankChangeCommand,
    PkBattlePreCommand, PkBattlePreNewCommand,
    PkBattleStartCommand, PkBattleStartNewCommand,
    PkBattlePunishEndCommand, PkBattleProcessNewCommand,
    PkBattleEndCommand, PkBattleProcessCommand, PkBattleFinalProcessCommand,
    PkBattleSettleNewCommand, PkBattleSettleCommand, PkBattleSettleV2Command, PkBattleSettleUserCommand,
    PkBattleEntranceCommand,
)
from .popular_rank_changed import PopularRankChangedCommand
from .preparing import PreparingCommand
from .recommend_card import RecommendCardCommand
from .ring_status_change import RingStatusChangeCommand, RingStatusChangeCommandV2
from .room_admin_entrace import RoomAdminEntranceCommand
from .room_admins import RoomAdminsCommand
from .room_block_msg import RoomBlockCommand
from .room_change import RoomChangeCommand
from .room_real_time_message_update import RoomRealTimeMessageUpdateCommand
from .room_silent import RoomSilentOnCommand, RoomSilentOffCommand
from .room_skin_msg import RoomSkinCommand
from .send_gift import GiftCommand
from .shopping_bubbles_style import ShoppingBubblesStyleCommand
from .shopping_cart_show import ShoppingCartShowCommand
from .shopping_explain_card import ShoppingExplainCardCommand
from .special_gift import SpecialGiftCommand
from .stop_live_room_list import StopLiveRoomListCommand
from .super_chat_entrance import SuperChatEntranceCommand
from .super_chat_message import SuperChatCommand
from .super_chat_message_delete import SuperChatDeleteCommand
from .sys_msg import SysMsgCommand
from .trading_score import TradingScoreCommand
from .user_toast_msg import UserToastMsgCommand
from .video_connection import VideoConnectionMsgCommand, VideoConnectionJoinEndCommand, VideoConnectionJoinStartCommand
from .voice_join import VoiceJoinStatusCommand
from .warning import WarningCommand
from .watched_change import WatchedChangeCommand
from .widget_gift_star_process import WidgetGiftStarProcessCommand

AnnotatedCommandModel = Annotated[Union[
    ActivityBannerChangeCommand, ActivityBannerChangeV2Command,
    AnchorHelperDanmuCommand,
    AnchorLotStartCommand, AnchorLotCheckStatusCommand, AnchorLotEndCommand, AnchorLotAwardCommand,
    AreaRankChangedCommand,
    CardMsgCommand,
    ComboEndCommand,
    ComboSendCommand,
    CommonNoticeDanmakuCommand,
    CutOffCommand,
    DanmuAggregationCommand,
    DanmakuCommand,
    EntryEffectCommand, EntryEffectMustReceiveCommand,
    FullScreenSpecialEffectCommand,
    GiftStarProcessCommand,
    GotoBuyFlowCommand,
    GuardBuyCommand,
    GuardHonorThousandCommand,
    HeartbeatCommand,
    HotBuyNumCommand,
    HotRankSettlementCommand, HotRankSettlementV2Command,
    HotRoomNotifyCommand,
    InteractWordCommand,
    LikeInfoV3UpdateCommand, LikeInfoV3ClickCommand, LikeInfoV3NoticeCommand,
    LiveCommand,
    LiveMultiViewChangeCommand,
    LivePanelChangeCommand,
    LogInNoticeCommand,
    MessageboxUserGainMedalCommand,
    MessageboxUserMedalChangeCommand,
    NoticeMsgCommand,
    OnlineRankCountCommand,
    PkBattleRankChangeCommand,
    PkBattlePreCommand, PkBattlePreNewCommand,
    PkBattleStartCommand, PkBattleStartNewCommand,
    PkBattlePunishEndCommand, PkBattleProcessNewCommand,
    PkBattleEndCommand, PkBattleProcessCommand, PkBattleFinalProcessCommand,
    PkBattleSettleNewCommand, PkBattleSettleCommand, PkBattleSettleV2Command, PkBattleSettleUserCommand,
    PkBattleEntranceCommand,
    PopularRankChangedCommand,
    PreparingCommand,
    RecommendCardCommand,
    RingStatusChangeCommand, RingStatusChangeCommandV2,
    RoomAdminEntranceCommand,
    RoomAdminsCommand,
    RoomBlockCommand,
    RoomChangeCommand,
    RoomRealTimeMessageUpdateCommand,
    RoomSilentOnCommand, RoomSilentOffCommand,
    RoomSkinCommand,
    GiftCommand,
    ShoppingBubblesStyleCommand,
    ShoppingCartShowCommand,
    ShoppingExplainCardCommand,
    SpecialGiftCommand,
    StopLiveRoomListCommand,
    SuperChatEntranceCommand,
    SuperChatCommand,
    SuperChatDeleteCommand,
    SysMsgCommand,
    TradingScoreCommand,
    UserToastMsgCommand,
    VideoConnectionMsgCommand, VideoConnectionJoinEndCommand, VideoConnectionJoinStartCommand,
    VoiceJoinStatusCommand,
    WarningCommand,
    WatchedChangeCommand,
    WidgetGiftStarProcessCommand
], Field(discriminator='cmd')]

__all__ = (
    'ActivityBannerChangeCommand', 'ActivityBannerChangeV2Command',
    'AnchorHelperDanmuCommand',
    'AnchorLotStartCommand', 'AnchorLotCheckStatusCommand', 'AnchorLotEndCommand', 'AnchorLotAwardCommand',
    'AreaRankChangedCommand',
    'CardMsgCommand',
    'ComboEndCommand',
    'ComboSendCommand',
    'CommonNoticeDanmakuCommand',
    'CutOffCommand',
    'DanmuAggregationCommand',
    'DanmakuCommand',
    'EntryEffectCommand', 'EntryEffectMustReceiveCommand',
    'FullScreenSpecialEffectCommand',
    'GiftStarProcessCommand',
    'GotoBuyFlowCommand',
    'GuardBuyCommand',
    'GuardHonorThousandCommand',
    'HeartbeatCommand',
    'HotBuyNumCommand',
    'HotRankSettlementCommand', 'HotRankSettlementV2Command',
    'HotRoomNotifyCommand',
    'InteractWordCommand',
    'LikeInfoV3UpdateCommand', 'LikeInfoV3ClickCommand', 'LikeInfoV3NoticeCommand',
    'LiveCommand',
    'LiveMultiViewChangeCommand',
    'LivePanelChangeCommand',
    'LogInNoticeCommand',
    'MessageboxUserGainMedalCommand',
    'MessageboxUserMedalChangeCommand',
    'NoticeMsgCommand',
    'OnlineRankCountCommand',
    'PreparingCommand',
    'PkBattleRankChangeCommand',
    'PkBattlePreCommand', 'PkBattlePreNewCommand',
    'PkBattleStartCommand', 'PkBattleStartNewCommand',
    'PkBattlePunishEndCommand', 'PkBattleProcessNewCommand',
    'PkBattleEndCommand', 'PkBattleProcessCommand', 'PkBattleFinalProcessCommand',
    'PkBattleSettleNewCommand', 'PkBattleSettleCommand', 'PkBattleSettleV2Command', 'PkBattleSettleUserCommand',
    'PkBattleEntranceCommand',
    'RecommendCardCommand',
    'RingStatusChangeCommand', 'RingStatusChangeCommandV2',
    'RoomAdminEntranceCommand',
    'RoomAdminsCommand',
    'RoomBlockCommand',
    'RoomChangeCommand',
    'RoomRealTimeMessageUpdateCommand',
    'RoomSilentOnCommand', 'RoomSilentOffCommand',
    'RoomSkinCommand',
    'GiftCommand',
    'ShoppingBubblesStyleCommand',
    'ShoppingCartShowCommand',
    'ShoppingExplainCardCommand',
    'SpecialGiftCommand',
    'StopLiveRoomListCommand',
    'SuperChatEntranceCommand',
    'SuperChatCommand',
    'SuperChatDeleteCommand',
    'SysMsgCommand',
    'TradingScoreCommand',
    'UserToastMsgCommand',
    'VideoConnectionMsgCommand', 'VideoConnectionJoinEndCommand', 'VideoConnectionJoinStartCommand',
    'VoiceJoinStatusCommand',
    'WarningCommand',
    'WatchedChangeCommand',
    'WidgetGiftStarProcessCommand',
    'AnnotatedCommandModel', 'Summary', 'Summarizer', 'CommandModel',
)
