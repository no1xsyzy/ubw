# -*- coding: utf-8 -*-
from typing import Annotated, Union

from ._base import *
from .anchor_lot import AnchorLotStartCommand, AnchorLotCheckStatusCommand, AnchorLotEndCommand, AnchorLotAwardCommand
from .danmu_msg import DanmakuCommand
from .entry_effect import EntryEffectCommand
from .guard_buy import GuardBuyCommand
from .guard_honor_thousand import GuardHonorThousandCommand
from .heartbeat import HeartbeatCommand
from .hot_rank_settlement import HotRankSettlementCommand, HotRankSettlementV2Command
from .interact_word import InteractWordCommand
from .live import LiveCommand
from .live_multi_view_change import LiveMultiViewChangeCommand
from .notice_msg import NoticeMsgCommand
from .online_rank_count import OnlineRankCountCommand
from .preparing import PreparingCommand
from .ring_status_change import RingStatusChangeCommand, RingStatusChangeCommandV2
from .room_admin_entrace import RoomAdminEntranceCommand
from .room_admins import RoomAdminsCommand
from .room_block_msg import RoomBlockCommand
from .room_change import RoomChangeCommand
from .room_skin_msg import RoomSkinCommand
from .send_gift import GiftCommand
from .special_gift import SpecialGiftCommand
from .stop_live_room_list import StopLiveRoomListCommand
from .super_chat_message import SuperChatCommand
from .super_chat_message_delete import SuperChatDeleteCommand
from .sys_msg import SysMsgCommand
from .trading_score import TradingScoreCommand
from .user_toast_msg import UserToastMsgCommand
from .warning import WarningCommand
from .watched_change import WatchedChangeCommand
from .widget_gift_star_process import WidgetGiftStarProcessCommand

AnnotatedCommandModel = Annotated[Union[tuple(CommandModel.__subclasses__())], Field(discriminator='cmd')]

__all__ = (
    *(cmdm.__name__ for cmdm in CommandModel.__subclasses__()),
    'AnnotatedCommandModel', 'Summary', 'Summarizer', 'CommandModel',
)
