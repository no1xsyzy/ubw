# -*- coding: utf-8 -*-
import logging
from contextvars import ContextVar
from typing import *

from pydantic import parse_obj_as, ValidationError

from . import client as client_
from . import models

__all__ = (
    'BaseHandler',
    'ctx_client',
    'ctx_command',
)

logger = logging.getLogger('blivedm')

# 常见可忽略的cmd
IGNORED_CMDS = (
    # 'AREA_RANK_CHANGED',
    # 'COMBO_SEND',
    # 'COMMON_NOTICE_DANMAKU',
    # 'DANMU_AGGREGATION',
    'FULL_SCREEN_SPECIAL_EFFECT',
    # 'GIFT_STAR_PROCESS',
    'HOT_RANK_CHANGED',
    'HOT_RANK_CHANGED_V2',
    'HOT_RANK_SETTLEMENT',
    'HOT_RANK_SETTLEMENT_V2',
    'LIKE_INFO_V3_CLICK',
    'LIKE_INFO_V3_UPDATE',
    'LIVE_INTERACTIVE_GAME',
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
    'SUPER_CHAT_MESSAGE_JPN',
    'VOICE_JOIN_LIST',
    'VOICE_JOIN_ROOM_COUNT_INFO',
    'VOICE_JOIN_SWITCH',
    'WIDGET_BANNER',
    'WIDGET_GIFT_STAR_PROCESS',
)

ctx_client = ContextVar[client_.BLiveClient]('client')
ctx_command = ContextVar[Union[dict, models.CommandModel]]('command')


class BaseHandler:
    """
    一个简单的消息处理器实现，带消息分发和消息类型转换。继承并重写on_xxx方法即可实现自己的处理器
    """

    CmdCallback = Callable[[client_.BLiveClient, Union[
        models.CommandModel, dict]], Coroutine[None, None, None]]
    _cmd_callbacks: dict[str, Union[None, CmdCallback]]

    def __init__(self, **p):
        self._cmd_callbacks = {}
        for ignore in IGNORED_CMDS:
            self._cmd_callbacks[ignore] = None

    async def handle(self, client: client_.BLiveClient, command: dict):
        tok_client_set = ctx_client.set(client)
        tok_command_set = ctx_command.set(command)
        try:
            cmd = command.get('cmd', '')

            # 2019-5-29 B站弹幕升级新增了参数
            pos = cmd.find(':')
            if pos != -1:
                cmd = cmd[:pos]

            # 手工指定回调
            if cmd in self._cmd_callbacks:
                callback = self._cmd_callbacks[cmd]
                if callback is not None:
                    logger.debug(f"got a {cmd}, processed with {callback.__name__}")
                    return await callback(client, command)
                else:
                    logger.debug(f"got a {cmd}, processed with ignore")
                    return

            try:
                model: models.CommandModel = parse_obj_as(models.AnnotatedCommandModel, command)
                ctx_command.reset(tok_command_set)
                tok_command_set = ctx_command.set(model)
                cmd = model.cmd.lower().strip("_")
                if hasattr(self, f'on_{cmd}'):
                    callback = getattr(self, f'on_{cmd}')
                    logger.debug(f"got a {cmd}, processed with {callback.__qualname__}")
                    return await callback(client, model)
                else:
                    logger.debug(f"got a {cmd}, processed with {self.on_else.__qualname__}")
                    return await self.on_else(client, model)
            except ValidationError:
                logger.debug(f"got a {cmd}, processed with {self.on_unknown_cmd.__qualname__}")
                await self.on_unknown_cmd(client, command)
        except Exception:
            logger.debug(f"got a {command.get('cmd', '')}, and error in processing")
            logger.exception(f"Error command: {command!r}")
        finally:
            ctx_command.reset(tok_command_set)
            ctx_client.reset(tok_client_set)

    async def on_unknown_cmd(self, client: client_.BLiveClient, command: dict):
        logger.warning(f"unknown cmd {command.get('cmd', None)} {command}")

    async def on_summary(self, client: client_.BLiveClient, model: models.Summary):
        """可摘要消息"""

    async def on_else(self, client: client_.BLiveClient, model: models.CommandModel):
        """未处理且未忽略消息"""
        if isinstance(model, models.Summarizer):
            return await self.on_summary(client, model.summarize())

    async def on_heartbeat(self, client: client_.BLiveClient, message: models.HeartbeatCommand):
        """收到心跳包（人气值）"""
        await self.on_else(client, message)

    async def on_danmu_msg(self, client: client_.BLiveClient, message: models.DanmakuCommand):
        """收到弹幕"""
        await self.on_else(client, message)

    async def on_send_gift(self, client: client_.BLiveClient, message: models.GiftCommand):
        """收到礼物"""
        await self.on_else(client, message)

    async def on_guard_buy(self, client: client_.BLiveClient, message: models.GuardBuyCommand):
        """有人上舰"""
        await self.on_else(client, message)

    async def on_super_chat_message(self, client: client_.BLiveClient, message: models.SuperChatCommand):
        """醒目留言"""
        await self.on_else(client, message)

    async def on_super_chat_message_delete(self, client: client_.BLiveClient, message: models.SuperChatDeleteCommand):
        """删除醒目留言"""
        await self.on_else(client, message)

    async def on_room_change(self, client: client_.BLiveClient, message: models.RoomChangeCommand):
        """房间信息改变"""
        await self.on_else(client, message)

    async def on_live(self, client: client_.BLiveClient, message: models.LiveCommand):
        """开始直播"""
        await self.on_else(client, message)

    async def on_preparing(self, client: client_.BLiveClient, message: models.PreparingCommand):
        """直播准备中"""
        await self.on_else(client, message)

    async def on_warning(self, client, message):
        """超管警告"""
        await self.on_else(client, message)

    async def on_hot_rank_settlement_v2(self, client: client_.BLiveClient, message: models.HotRankSettlementV2Command):
        await self.on_else(client, message)

    async def on_hot_rank_settlement(self, client: client_.BLiveClient, message: models.HotRankSettlementCommand):
        await self.on_else(client, message)

    async def on_room_block_msg(self, client: client_.BLiveClient, message: models.RoomBlockCommand):
        """观众被封禁"""
        await self.on_else(client, message)

    async def on_room_skin_msg(self, client: client_.BLiveClient, message: models.RoomSkinCommand):
        await self.on_else(client, message)

    async def on_trading_score(self, client: client_.BLiveClient, message: models.TradingScoreCommand):
        await self.on_else(client, message)

    async def on_room_admins(self, client: client_.BLiveClient, message: models.RoomAdminsCommand):
        """房管"""
        await self.on_else(client, message)

    async def on_room_admin_entrance(self, client: client_.BLiveClient, message: models.RoomAdminEntranceCommand):
        """新房管"""
        await self.on_else(client, message)

    async def on_ring_status_change(self, client: client_.BLiveClient, message: models.RingStatusChangeCommand):
        """未知"""
        await self.on_else(client, message)

    async def on_ring_status_change_v2(self, client: client_.BLiveClient, message: models.RingStatusChangeCommandV2):
        """未知"""
        await self.on_else(client, message)

    async def on_notice_msg(self, client: client_.BLiveClient, model: models.NoticeMsgCommand):
        """未知"""
        await self.on_else(client, model)
