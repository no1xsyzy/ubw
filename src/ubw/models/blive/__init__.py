# -*- coding: utf-8 -*-

from ._base import *
from .activity_banner_change import ActivityBannerChangeCommand
from .activity_banner_change_v2 import ActivityBannerChangeV2Command
from .admin_shield_keyword import AdminShieldKeywordCommand
from .anchor_broadcast import AnchorBroadcastCommand
from .anchor_ecommerce_status import AnchorEcommerceStatusCommand
from .anchor_helper_danmu import AnchorHelperDanmuCommand
from .anchor_lot import AnchorLotStartCommand, AnchorLotCheckStatusCommand, AnchorLotEndCommand, AnchorLotAwardCommand
from .area_rank_changed import AreaRankChangedCommand
from .benefit_status import BenefitStatusCommand
from .card_msg import CardMsgCommand
from .change_room_info import ChangeRoomInfoCommand
from .combo_end import ComboEndCommand
from .combo_send import ComboSendCommand
from .common_notice_danmaku import CommonNoticeDanmakuCommand
from .confirm_auto_follow import ConfirmAutoFollowCommand
from .cut_off import CutOffCommand
from .danmu_aggregation import DanmuAggregationCommand
from .danmu_msg import DanmakuCommand, Danmaku371111Command
from .dm_interaction import DmInteractionCommand
from .entry_effect import EntryEffectCommand, EntryEffectMustReceiveCommand
from .full_screen_special_effect import FullScreenSpecialEffectCommand
from .gift_board_red_dot import GiftBoardRedDotCommand
from .gift_panel_plan import GiftPanelPlanCommand
from .gift_star_process import GiftStarProcessCommand
from .goto_buy_flow import GotoBuyFlowCommand
from .guard_achievement_room import GuardAchievementRoomCommand
from .guard_benefit_receive import GuardBenefitReceiveCommand
from .guard_buy import GuardBuyCommand
from .guard_honor_thousand import GuardHonorThousandCommand
from .heartbeat import HeartbeatCommand
from .hot_buy_num import HotBuyNumCommand
from .hot_rank_settlement import HotRankSettlementCommand, HotRankSettlementV2Command
from .hot_room_notify import HotRoomNotifyCommand
from .interact_word import InteractWordCommand
from .like_guide_user import LikeGuideUserCommand
from .like_info import LikeInfoV3UpdateCommand, LikeInfoV3ClickCommand, LikeInfoV3NoticeCommand
from .little_message_box import LittleMessageBoxCommand
from .live import LiveCommand
from .live_interactive_game import LiveInteractiveGameCommand
from .live_multi_view_change import LiveMultiViewChangeCommand
from .live_open_platform_game import LiveOpenPlatformGameCommand
from .live_panel_change import LivePanelChangeCommand
from .live_panel_change_content import LivePanelChangeContentCommand
from .log_in_notice import LogInNoticeCommand
from .messagebox_user_gain_medal import MessageboxUserGainMedalCommand
from .messagebox_user_medal_change import MessageboxUserMedalChangeCommand
from .notice_msg import NoticeMsgCommand
from .official_room_event import OfficialRoomEventCommand
from .online_rank_count import OnlineRankCountCommand
from .online_rank_top3 import OnlineRankTop3Command
from .online_rank_v2 import OnlineRankV2Command
from .pk import (
    PkBattleRankChangeCommand,
    PkBattlePreCommand, PkBattlePreNewCommand,
    PkBattleStartCommand, PkBattleStartNewCommand,
    PkBattlePunishEndCommand, PkBattleProcessNewCommand,
    PkBattleEndCommand, PkBattleProcessCommand, PkBattleFinalProcessCommand,
    PkBattleSettleNewCommand, PkBattleSettleCommand, PkBattleSettleV2Command, PkBattleSettleUserCommand,
    PkBattleEntranceCommand,
    PkBattleMatchTimeoutCommand,
)
from .playtogether_icon_change import PlaytogetherIconChangeCommand
from .popular_rank_changed import PopularRankChangedCommand
from .popularity_red_pocket_new import PopularityRedPocketNewCommand
from .popularity_red_pocket_start import PopularityRedPocketStartCommand
from .popularity_red_pocket_winner_list import PopularityRedPocketWinnerListCommand
from .preparing import PreparingCommand
from .recommend_card import RecommendCardCommand
from .ring_status_change import RingStatusChangeCommand, RingStatusChangeCommandV2
from .room_admin import RoomAdminsCommand, RoomAdminEntranceCommand, RoomAdminRevokeCommand
from .room_block_msg import RoomBlockCommand
from .room_change import RoomChangeCommand
from .room_module_display import RoomModuleDisplayCommand
from .room_real_time_message_update import RoomRealTimeMessageUpdateCommand
from .room_silent import RoomSilentOnCommand, RoomSilentOffCommand
from .room_skin_msg import RoomSkinCommand
from .send_gift import GiftCommand
from .shopping_bubbles_style import ShoppingBubblesStyleCommand
from .shopping_cart_show import ShoppingCartShowCommand
from .shopping_explain_card import ShoppingExplainCardCommand
from .special_gift import SpecialGiftCommand
from .spread_order_over import SpreadOrderOverCommand
from .spread_order_start import SpreadOrderStartCommand
from .spread_show_feet import SpreadShowFeetCommand
from .spread_show_feet_v2 import SpreadShowFeetV2Command
from .stop_live_room_list import StopLiveRoomListCommand
from .studio_room_close import StudioRoomCloseCommand
from .super_chat_entrance import SuperChatEntranceCommand
from .super_chat_message import SuperChatCommand
from .super_chat_message_delete import SuperChatDeleteCommand
from .super_chat_message_jpn import SuperChatMessageJpnCommand
from .sys_msg import SysMsgCommand
from .trading_score import TradingScoreCommand
from .user_info_update import UserInfoUpdateCommand
from .user_panel_red_alarm import UserPanelRedAlarmCommand
from .user_task_progress import UserTaskProgressCommand
from .user_toast_msg import UserToastMsgCommand
from .video_connection import VideoConnectionMsgCommand, VideoConnectionJoinEndCommand, VideoConnectionJoinStartCommand
from .voice_join import VoiceJoinStatusCommand, VoiceJoinListCommand, VoiceJoinRoomCountInfoCommand
from .warning import WarningCommand
from .watched_change import WatchedChangeCommand
from .wealth_notify import WealthNotifyCommand
from .widget_banner import WidgetBannerCommand
from .widget_gift_star_process import WidgetGiftStarProcessCommand

AnnotatedCommandModel = Annotated[Union[
    ActivityBannerChangeCommand, ActivityBannerChangeV2Command,
    AdminShieldKeywordCommand,
    AnchorBroadcastCommand,
    AnchorEcommerceStatusCommand,
    AnchorHelperDanmuCommand,
    AnchorLotStartCommand, AnchorLotCheckStatusCommand, AnchorLotEndCommand, AnchorLotAwardCommand,
    AreaRankChangedCommand,
    BenefitStatusCommand,
    CardMsgCommand,
    ChangeRoomInfoCommand,
    ComboEndCommand,
    ComboSendCommand,
    CommonNoticeDanmakuCommand,
    ConfirmAutoFollowCommand,
    CutOffCommand,
    DanmuAggregationCommand,
    DanmakuCommand, Danmaku371111Command,
    DmInteractionCommand,
    EntryEffectCommand, EntryEffectMustReceiveCommand,
    FullScreenSpecialEffectCommand,
    GiftBoardRedDotCommand,
    GiftPanelPlanCommand,
    GiftStarProcessCommand,
    GotoBuyFlowCommand,
    GuardAchievementRoomCommand,
    GuardBenefitReceiveCommand,
    GuardBuyCommand,
    GuardHonorThousandCommand,
    HeartbeatCommand,
    HotBuyNumCommand,
    HotRankSettlementCommand, HotRankSettlementV2Command,
    HotRoomNotifyCommand,
    InteractWordCommand,
    LikeGuideUserCommand,
    LikeInfoV3UpdateCommand, LikeInfoV3ClickCommand, LikeInfoV3NoticeCommand,
    LittleMessageBoxCommand,
    LiveCommand,
    LiveInteractiveGameCommand,
    LiveMultiViewChangeCommand,
    LiveOpenPlatformGameCommand,
    LivePanelChangeCommand,
    LivePanelChangeContentCommand,
    LogInNoticeCommand,
    MessageboxUserGainMedalCommand,
    MessageboxUserMedalChangeCommand,
    NoticeMsgCommand,
    OfficialRoomEventCommand,
    OnlineRankCountCommand,
    OnlineRankTop3Command,
    OnlineRankV2Command,
    PkBattleRankChangeCommand,
    PkBattlePreCommand, PkBattlePreNewCommand,
    PkBattleStartCommand, PkBattleStartNewCommand,
    PkBattlePunishEndCommand, PkBattleProcessNewCommand,
    PkBattleEndCommand, PkBattleProcessCommand, PkBattleFinalProcessCommand,
    PkBattleSettleNewCommand, PkBattleSettleCommand, PkBattleSettleV2Command, PkBattleSettleUserCommand,
    PkBattleEntranceCommand,
    PkBattleMatchTimeoutCommand,
    PlaytogetherIconChangeCommand,
    PopularRankChangedCommand,
    PopularityRedPocketNewCommand,
    PopularityRedPocketStartCommand,
    PopularityRedPocketWinnerListCommand,
    PreparingCommand,
    RecommendCardCommand,
    RingStatusChangeCommand, RingStatusChangeCommandV2,
    RoomAdminsCommand, RoomAdminEntranceCommand, RoomAdminRevokeCommand,
    RoomBlockCommand,
    RoomChangeCommand,
    RoomModuleDisplayCommand,
    RoomRealTimeMessageUpdateCommand,
    RoomSilentOnCommand, RoomSilentOffCommand,
    RoomSkinCommand,
    GiftCommand,
    ShoppingBubblesStyleCommand,
    ShoppingCartShowCommand,
    ShoppingExplainCardCommand,
    SpecialGiftCommand,
    SpreadOrderOverCommand,
    SpreadOrderStartCommand,
    SpreadShowFeetCommand,
    SpreadShowFeetV2Command,
    StopLiveRoomListCommand,
    StudioRoomCloseCommand,
    SuperChatEntranceCommand,
    SuperChatCommand,
    SuperChatDeleteCommand,
    SuperChatMessageJpnCommand,
    SysMsgCommand,
    TradingScoreCommand,
    UserInfoUpdateCommand,
    UserPanelRedAlarmCommand,
    UserTaskProgressCommand,
    UserToastMsgCommand,
    VideoConnectionMsgCommand, VideoConnectionJoinEndCommand, VideoConnectionJoinStartCommand,
    VoiceJoinStatusCommand, VoiceJoinListCommand, VoiceJoinRoomCountInfoCommand,
    WarningCommand,
    WatchedChangeCommand,
    WealthNotifyCommand,
    WidgetBannerCommand,
    WidgetGiftStarProcessCommand
], Field(discriminator='cmd')]

__all__ = (
    'ActivityBannerChangeCommand', 'ActivityBannerChangeV2Command',
    'AdminShieldKeywordCommand',
    'AnchorBroadcastCommand',
    'AnchorEcommerceStatusCommand',
    'AnchorHelperDanmuCommand',
    'AnchorLotStartCommand', 'AnchorLotCheckStatusCommand', 'AnchorLotEndCommand', 'AnchorLotAwardCommand',
    'AreaRankChangedCommand',
    'BenefitStatusCommand',
    'CardMsgCommand',
    'ChangeRoomInfoCommand',
    'ComboEndCommand',
    'ComboSendCommand',
    'CommonNoticeDanmakuCommand',
    'ConfirmAutoFollowCommand',
    'CutOffCommand',
    'DanmuAggregationCommand',
    'DanmakuCommand', 'Danmaku371111Command',
    'DmInteractionCommand',
    'EntryEffectCommand', 'EntryEffectMustReceiveCommand',
    'FullScreenSpecialEffectCommand',
    'GiftBoardRedDotCommand',
    'GiftPanelPlanCommand',
    'GiftStarProcessCommand',
    'GotoBuyFlowCommand',
    'GuardAchievementRoomCommand',
    'GuardBenefitReceiveCommand',
    'GuardBuyCommand',
    'GuardHonorThousandCommand',
    'HeartbeatCommand',
    'HotBuyNumCommand',
    'HotRankSettlementCommand', 'HotRankSettlementV2Command',
    'HotRoomNotifyCommand',
    'InteractWordCommand',
    'LikeGuideUserCommand',
    'LikeInfoV3UpdateCommand', 'LikeInfoV3ClickCommand', 'LikeInfoV3NoticeCommand',
    'LittleMessageBoxCommand',
    'LiveCommand',
    'LiveInteractiveGameCommand',
    'LiveMultiViewChangeCommand',
    'LiveOpenPlatformGameCommand',
    'LivePanelChangeCommand',
    'LivePanelChangeContentCommand',
    'LogInNoticeCommand',
    'MessageboxUserGainMedalCommand',
    'MessageboxUserMedalChangeCommand',
    'NoticeMsgCommand',
    'OfficialRoomEventCommand',
    'OnlineRankCountCommand',
    'OnlineRankTop3Command',
    'OnlineRankV2Command',
    'PreparingCommand',
    'PkBattleRankChangeCommand',
    'PkBattlePreCommand', 'PkBattlePreNewCommand',
    'PkBattleStartCommand', 'PkBattleStartNewCommand',
    'PkBattlePunishEndCommand', 'PkBattleProcessNewCommand',
    'PkBattleEndCommand', 'PkBattleProcessCommand', 'PkBattleFinalProcessCommand',
    'PkBattleSettleNewCommand', 'PkBattleSettleCommand', 'PkBattleSettleV2Command', 'PkBattleSettleUserCommand',
    'PkBattleEntranceCommand',
    'PkBattleMatchTimeoutCommand',
    'PlaytogetherIconChangeCommand',
    'PopularityRedPocketNewCommand',
    'PopularityRedPocketStartCommand',
    'PopularityRedPocketWinnerListCommand',
    'RecommendCardCommand',
    'RingStatusChangeCommand', 'RingStatusChangeCommandV2',
    'RoomAdminsCommand', 'RoomAdminEntranceCommand', 'RoomAdminRevokeCommand',
    'RoomBlockCommand',
    'RoomChangeCommand',
    'RoomModuleDisplayCommand',
    'RoomRealTimeMessageUpdateCommand',
    'RoomSilentOnCommand', 'RoomSilentOffCommand',
    'RoomSkinCommand',
    'GiftCommand',
    'ShoppingBubblesStyleCommand',
    'ShoppingCartShowCommand',
    'ShoppingExplainCardCommand',
    'SpecialGiftCommand',
    'SpreadOrderOverCommand',
    'SpreadOrderStartCommand',
    'SpreadShowFeetCommand',
    'SpreadShowFeetV2Command',
    'StopLiveRoomListCommand',
    'StudioRoomCloseCommand',
    'SuperChatEntranceCommand',
    'SuperChatCommand',
    'SuperChatDeleteCommand',
    'SuperChatMessageJpnCommand',
    'SysMsgCommand',
    'TradingScoreCommand',
    'UserInfoUpdateCommand',
    'UserPanelRedAlarmCommand',
    'UserTaskProgressCommand',
    'UserToastMsgCommand',
    'VideoConnectionMsgCommand', 'VideoConnectionJoinEndCommand', 'VideoConnectionJoinStartCommand',
    'VoiceJoinStatusCommand', 'VoiceJoinListCommand', 'VoiceJoinRoomCountInfoCommand',
    'WarningCommand',
    'WatchedChangeCommand',
    'WealthNotifyCommand',
    'WidgetBannerCommand',
    'WidgetGiftStarProcessCommand',
    'AnnotatedCommandModel', 'Summary', 'Summarizer', 'CommandModel',
)