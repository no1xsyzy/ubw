# -*- coding: utf-8 -*-
import asyncio
import inspect
import logging
import os
import time
import warnings
from functools import cached_property
from typing import *

import rich
import sentry_sdk
from pydantic import ValidationError, BaseModel, TypeAdapter
from rich.markup import escape

from .. import models
from ..clients import LiveClientABC

__all__ = (
    'BaseHandler',
    'Literal',
    'models',
    'rich', 'escape',
)

logger = logging.getLogger('ubw.handlers._base')

ANNOTATED_COMMAND_ADAPTER = TypeAdapter(models.AnnotatedCommandModel)

DEBUGGING_TOO_LONG = os.environ.get('DEBUGGING_TOO_LONG', '') == '1'


def _func_info(func: Callable):
    if inspect.iscode(func):
        return f"{func!r} ({func.co_filename}:{func.co_firstlineno})"
    elif inspect.isfunction(func):
        return f"{func!r} ({func.__code__.co_filename}:{func.__code__.co_firstlineno})"
    elif inspect.ismethod(func):
        return f"{func!r} ({func.__func__.__code__.co_filename}:{func.__func__.__code__.co_firstlineno})"
    elif inspect.isbuiltin(func):
        return f"{func!r} (builtin)"
    return f"{func!r} (???:???)"


class BaseHandler(BaseModel):
    cls: str
    ignored_cmd: list[str] = []

    def start(self, client: LiveClientABC):
        pass

    async def astart(self, client: LiveClientABC):
        pass

    if DEBUGGING_TOO_LONG:
        async def handle(self, client: LiveClientABC, command: dict):
            start = time.time()
            await self.process_one(client, command)
            if time.time() - start > 1:
                warnings.warn(f"command `{command['cmd']}` process too long (>1s)")
    else:
        async def handle(self, client: LiveClientABC, command: dict):
            await self.process_one(client, command)

    async def process_one(self, client: LiveClientABC, command: dict):
        try:
            cmd = command.get('cmd', '')

            # 2019-5-29 B站弹幕升级新增了参数
            pos = cmd.find(':')
            if pos != -1:
                cmd = cmd[:pos]

            # 强硬忽略
            if cmd in self.ignored_cmd:
                logger.debug(f"got a {cmd}, processed with ignore")
                return

            try:
                model: models.CommandModel = ANNOTATED_COMMAND_ADAPTER.validate_python(command)
            except ValidationError as e:
                logger.debug(f"got a {cmd}, processed with {_func_info(self.on_unknown_cmd)}")
                return await self.on_unknown_cmd(client, command, e)
            else:
                return await self.on_known_cmd(client, model)
        except Exception:
            logger.debug(f"got a {command.get('cmd', '')}, and error in processing")
            logger.exception(f"Error command: {command!r}")

    async def on_known_cmd(self, client: LiveClientABC, model: models.CommandModel):
        """默认的 dispatcher，自省寻找 on_{model.cmd}"""
        cmd = model.cmd.lower().split(":", 1)[0]
        if hasattr(self, f'on_{cmd}'):
            callback = getattr(self, f'on_{cmd}')
            logger.debug(f"got a {cmd}, processing with {_func_info(callback)})")
            return await callback(client, model)
        elif isinstance(model, models.Summarizer):
            logger.debug(f"got a {cmd}, summarized and processing with {_func_info(self.on_summary)})")
            return await self.on_summary(client, model.summarize())
        else:
            logger.debug(f"got a {cmd}, processing with {_func_info(self.on_else)})")
            return await self.on_else(client, model)

    async def on_unknown_cmd(self, client: LiveClientABC, command: dict, err: ValidationError):
        import json
        import aiofiles.os
        cmd = command.get('cmd', None)
        await aiofiles.os.makedirs("output/unknown_cmd", exist_ok=True)
        async with aiofiles.open(f"output/unknown_cmd/{cmd}.json", mode='a', encoding='utf-8') as afp:
            await afp.write(json.dumps(command, indent=2, ensure_ascii=False))
        error_details = err.errors(include_url=False)
        sentry_sdk.capture_event(
            event={'level': 'warning', 'message': f'error parsing command {cmd}'},
            user={'id': client.user_ident},
            contexts={'ValidationError': {'command': command, 'error': error_details}},
            tags={'handler': self.cls, 'type': 'command-parsing',
                  'cmd': cmd, 'room_id': client.room_id},
        )

    async def on_summary(self, client: LiveClientABC, summary: models.Summary):
        """可摘要消息"""
        await self.on_else(client, summary.raw)

    async def on_maybe_summarizer(self, client: LiveClientABC, model: models.CommandModel):
        if isinstance(model, models.Summarizer):
            return await self.on_summary(client, model.summarize())
        else:
            return await self.on_else(client, model)

    async def on_else(self, client: LiveClientABC, model: models.CommandModel):
        """未处理、不可摘要消息"""

    async def on_x_ubw_heartbeat(self, client: LiveClientABC, message: models.XHeartbeatCommand):
        """收到心跳包（人气值）"""
        await self.on_maybe_summarizer(client, message)

    async def on_danmu_msg(self, client: LiveClientABC, message: models.DanmakuCommand):
        """收到弹幕"""
        await self.on_maybe_summarizer(client, message)

    async def on_send_gift(self, client: LiveClientABC, message: models.GiftCommand):
        """收到礼物"""
        await self.on_maybe_summarizer(client, message)

    async def on_guard_buy(self, client: LiveClientABC, message: models.GuardBuyCommand):
        """有人上舰"""
        await self.on_maybe_summarizer(client, message)

    async def on_super_chat_message(self, client: LiveClientABC, message: models.SuperChatCommand):
        """醒目留言"""
        await self.on_maybe_summarizer(client, message)

    async def on_super_chat_message_delete(self, client: LiveClientABC, message: models.SuperChatDeleteCommand):
        """删除醒目留言"""
        await self.on_maybe_summarizer(client, message)

    async def on_room_change(self, client: LiveClientABC, message: models.RoomChangeCommand):
        """房间信息改变"""
        await self.on_maybe_summarizer(client, message)

    async def on_live(self, client: LiveClientABC, message: models.LiveCommand):
        """开始直播"""
        await self.on_maybe_summarizer(client, message)

    async def on_preparing(self, client: LiveClientABC, message: models.PreparingCommand):
        """直播准备中"""
        await self.on_maybe_summarizer(client, message)

    async def on_warning(self, client: LiveClientABC, message: models.WarningCommand):
        """超管警告"""
        await self.on_maybe_summarizer(client, message)

    async def on_hot_rank_settlement_v2(self, client: LiveClientABC, message: models.HotRankSettlementV2Command):
        await self.on_maybe_summarizer(client, message)

    async def on_hot_rank_settlement(self, client: LiveClientABC, message: models.HotRankSettlementCommand):
        await self.on_maybe_summarizer(client, message)

    async def on_room_block_msg(self, client: LiveClientABC, message: models.RoomBlockCommand):
        """观众被封禁"""
        await self.on_maybe_summarizer(client, message)

    async def on_room_skin_msg(self, client: LiveClientABC, message: models.RoomSkinCommand):
        await self.on_maybe_summarizer(client, message)

    async def on_trading_score(self, client: LiveClientABC, message: models.TradingScoreCommand):
        await self.on_maybe_summarizer(client, message)

    async def on_room_admins(self, client: LiveClientABC, message: models.RoomAdminsCommand):
        """房管"""
        await self.on_maybe_summarizer(client, message)

    async def on_room_admin_entrance(self, client: LiveClientABC, message: models.RoomAdminEntranceCommand):
        """新房管"""
        await self.on_maybe_summarizer(client, message)

    async def on_ring_status_change(self, client: LiveClientABC, message: models.RingStatusChangeCommand):
        """未知"""
        await self.on_maybe_summarizer(client, message)

    async def on_ring_status_change_v2(self, client: LiveClientABC, message: models.RingStatusChangeCommandV2):
        """未知"""
        await self.on_maybe_summarizer(client, message)

    async def on_notice_msg(self, client: LiveClientABC, model: models.NoticeMsgCommand):
        """未知"""
        await self.on_maybe_summarizer(client, model)

    async def on_interact_word(self, client: LiveClientABC, model: models.InteractWordCommand):
        """进入，关注，分享，特别关注，互相关注"""
        await self.on_maybe_summarizer(client, model)

    async def on_card_msg(self, client: LiveClientABC, model: models.CardMsgCommand):
        await self.on_maybe_summarizer(client, model)

    async def on_anchor_helper_danmu(self, client: LiveClientABC, model: models.AnchorHelperDanmuCommand):
        await self.on_maybe_summarizer(client, model)


class QueuedProcessorMixin(BaseHandler):
    """通过添加一个队列来处理"""
    _process_task: asyncio.Task | None = None

    @cached_property
    def _queue(self) -> asyncio.Queue[tuple[LiveClientABC, dict]]:
        return asyncio.Queue()

    def start(self, client):
        self._process_task = asyncio.create_task(self.t_process())
        super().start(client)

    async def handle(self, client: LiveClientABC, command: dict):
        await self._queue.put((client, command))
        qsize = self._queue.qsize()
        if qsize > 20:
            logger.warning(f'CANNOT KEEP UP queue size {qsize} > 20')

    async def t_process(self):
        while True:
            client, command = await self._queue.get()
            await self.process_one(client, command)
