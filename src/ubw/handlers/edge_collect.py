import asyncio
import json
import logging

import aiofiles

from ._base import *

logger = logging.getLogger('edge_collect')


class EdgeCollector(BaseHandler):
    cls: Literal['edge_collect'] = 'edge_collect'
    _living: bool = False
    _sharder_task: asyncio.Task | None = None

    async def process_one(self, client, command):
        cmd = command.get('cmd', '')

        reason = None
        if cmd == 'DANMU_MSG:3:7:1:1:1:1':
            if len(command['info']) != 17:
                reason = 'DANMU_MSG371111.info.length'
        elif cmd == 'DANMU_MSG':
            if command['info'][0][0] != 0:
                reason = 'DANMU_MSG.info.0.0'
            elif command['info'][0][6] != 0:
                reason = 'DANMU_MSG.info.0.6'
            elif command['info'][0][8] != 0:
                reason = 'DANMU_MSG.info.0.8'
            elif command['info'][0][14] != "{}":
                reason = 'DANMU_MSG.info.0.14'
            elif command['info'][0][16] != {"activity_identity": "", "activity_source": 0, "not_show": 0}:
                reason = 'DANMU_MSG.info.0.16'
            elif command['info'][0][17] not in {0, 4, 42, 43}:
                reason = 'DANMU_MSG.info.0.17'
            elif len(command['info'][0]) != 18:
                reason = 'DANMU_MSG.info.0.length'
            elif command['info'][3]:
                if command['info'][3][5] != '':
                    reason = 'MedalInfo.special'
            elif command['info'][4][1] != 0:
                reason = 'DANMU_MSG.info.4.1'
            elif command['info'][4][4] != 0:
                reason = 'DANMU_MSG.info.4.4'
            elif command['info'][10] != 0:
                reason = 'DANMU_MSG.info.10'
            elif command['info'][11] != 0:
                reason = 'DANMU_MSG.info.11'
            elif command['info'][12] is not None:
                reason = 'DANMU_MSG.info.12'
            elif command['info'][13] is not None:
                reason = 'DANMU_MSG.info.13'
            elif command['info'][14] != 0:
                reason = 'DANMU_MSG.info.14'
            elif len(command['info'][16]) != 1:
                reason = 'DANMU_MSG.info.16.length'
            elif len(command['info']) != 18:
                reason = 'DANMU_MSG.info.length'
        elif cmd in ['COMBO_SEND',
                     'SEND_GIFT',
                     'SUPER_CHAT_MESSAGE',
                     'SUPER_CHAT_MESSAGE_JPN'] and command['data']['medal_info']['special'] != '':
            reason = 'MedalInfo.special'

        if reason:
            logger.info(f"collected a {cmd}, {reason=}")
            async with aiofiles.open(f"output/edge_collect/{reason}.json", mode='a', encoding='utf-8') as afp:
                await afp.write(json.dumps(command, indent=2, ensure_ascii=False))
