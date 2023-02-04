# -*- coding: utf-8 -*-
import logging
from typing import *

from pydantic import parse_obj_as, ValidationError, Field

from . import client as client_
from . import models

__all__ = (
    'HandlerInterface',
    'BaseHandler',
)

logger = logging.getLogger('blivedm')

# 常见可忽略的cmd
IGNORED_CMDS = (
    'AREA_RANK_CHANGED',
    'COMBO_SEND',
    'COMMON_NOTICE_DANMAKU',
    'DANMU_AGGREGATION',
    'ENTRY_EFFECT',
    'FULL_SCREEN_SPECIAL_EFFECT',
    'GIFT_STAR_PROCESS',
    'GUARD_HONOR_THOUSAND',
    'HOT_RANK_CHANGED',
    'HOT_RANK_CHANGED_V2',
    'HOT_RANK_SETTLEMENT',
    'HOT_RANK_SETTLEMENT_V2',
    'INTERACT_WORD',
    'LIKE_INFO_V3_CLICK',
    'LIKE_INFO_V3_UPDATE',
    'LIVE_INTERACTIVE_GAME',
    'NOTICE_MSG',
    'ONLINE_RANK_COUNT',
    'ONLINE_RANK_TOP3',
    'ONLINE_RANK_V2',
    'PK_BATTLE_END',
    'PK_BATTLE_ENTRANCE',
    'PK_BATTLE_FINAL_PROCESS',
    'PK_BATTLE_PROCESS',
    'PK_BATTLE_PROCESS_NEW',
    'PK_BATTLE_SETTLE',
    'PK_BATTLE_SETTLE_USER',
    'PK_BATTLE_SETTLE_V2',
    'POPULAR_RANK_CHANGED',
    'POPULARITY_RED_POCKET_NEW',
    'POPULARITY_RED_POCKET_START',
    'POPULARITY_RED_POCKET_WINNER_LIST',
    'ROOM_REAL_TIME_MESSAGE_UPDATE',
    'STOP_LIVE_ROOM_LIST',
    'SUPER_CHAT_MESSAGE_JPN',
    'SYS_MSG',
    'TRADING_SCORE',
    'USER_TOAST_MSG',
    'VOICE_JOIN_LIST',
    'VOICE_JOIN_ROOM_COUNT_INFO',
    'VOICE_JOIN_SWITCH',
    'WATCHED_CHANGE',
    'WIDGET_BANNER',
)

# 已打日志的未知cmd
logged_unknown_cmds = set()


class HandlerInterface(Protocol):
    """直播消息处理器接口"""

    async def handle(self, client: client_.BLiveClient, command: dict):
        raise NotImplementedError


class BaseHandler:
    """
    一个简单的消息处理器实现，带消息分发和消息类型转换。继承并重写on_xxx方法即可实现自己的处理器
    """

    def __heartbeat_callback(self, client: client_.BLiveClient, command: dict):
        return self.on_heartbeat(client, models.HeartbeatMessage.from_command(command['data']))

    def __init__(self, **p):
        self._cmd_callbacks = {
            '_HEARTBEAT': self.__heartbeat_callback,
        }
        for ignore in IGNORED_CMDS:
            self._cmd_callbacks[ignore] = None

    async def handle(self, client: client_.BLiveClient, command: dict):
        cmd = command.get('cmd', '')
        pos = cmd.find(':')  # 2019-5-29 B站弹幕升级新增了参数
        if pos != -1:
            cmd = cmd[:pos]

        if cmd in self._cmd_callbacks:
            callback = self._cmd_callbacks[cmd]
            if callback is not None:
                return await callback(client, command)
            else:
                return

        try:
            model: models.CommandModel = parse_obj_as(
                Annotated[
                    Union[tuple(models.CommandModel.__subclasses__())],
                    Field(discriminator='cmd')],
                command)
            if hasattr(self, "on_" + model.cmd.lower()):
                return await getattr(self, "on_" + model.cmd.lower())(client, model)
            else:
                return await self.on_else(client, model)
        except ValidationError:
            self._cmd_callbacks[cmd] = None  # ignores more commands
            logger.warning(f"[{client.room_id}] unknown cmd `{cmd}`")
            logger.exception(command)

    async def on_else(self, client: client_.BLiveClient, model: Union[tuple(models.CommandModel.__subclasses__())]):
        """其他种类未忽略消息"""

    async def on_heartbeat(self, client: client_.BLiveClient, message: models.HeartbeatMessage):
        """收到心跳包（人气值）"""

    async def on_danmu_msg(self, client: client_.BLiveClient, message: models.DanmakuCommand):
        """收到弹幕"""

    async def on_send_gift(self, client: client_.BLiveClient, message: models.GiftCommand):
        """收到礼物"""

    async def on_buy_guard(self, client: client_.BLiveClient, message: models.GuardBuyCommand):
        """有人上舰"""

    async def on_super_chat(self, client: client_.BLiveClient, message: models.SuperChatCommand):
        """醒目留言"""

    async def on_super_chat_delete(self, client: client_.BLiveClient, message: models.SuperChatDeleteCommand):
        """删除醒目留言"""

    async def on_room_change(self, client: client_.BLiveClient, message: models.RoomChangeCommand):
        """房间信息改变"""

    async def on_warning(self, client, message):
        """超管警告"""

    async def on_live(self, client: client_.BLiveClient, message: models.LiveCommand):
        """开始直播"""

    async def on_preparing(self, client: client_.BLiveClient, message: models.PreparingCommand):
        """直播准备中"""

    async def on_room_block_msg(self, client: client_.BLiveClient, message: models.RoomBlockCommand):
        """观众被封禁"""
