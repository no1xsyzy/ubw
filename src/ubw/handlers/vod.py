import csv
import re
from datetime import timedelta, datetime
from functools import cached_property
from operator import itemgetter
from pathlib import Path

from bilibili_api.video import Video

from ._base import *
from ..clients import LiveClientABC, BilibiliClient
from ..ui.stream_view import StreamView, Richy, Record, User, PlainText, Anchor

owner = itemgetter('name', 'mid', 'face')


class VodHandler(BaseHandler):
    cls: Literal['vod'] = 'vod'

    save_csv: str | None = None

    # DI
    ui: StreamView = Richy()
    owned_ui: bool = True

    @cached_property
    def target(self) -> Path | None:
        if self.save_csv is None:
            return None
        p = self.save_csv
        if "{date}" in p:
            p.replace("{date}", datetime.today().strftime("%Y%m%d"))
        return Path(self.save_csv)

    async def on_super_chat_message(self, client: LiveClientABC, message: models.SuperChatCommand):
        bclient: BilibiliClient = client.bilibili_client
        for bvid in re.findall(r"BV\w{10}", message.data.message):
            detail = await Video(bvid, credential=await bclient.get_credential()).get_detail()
            duration = timedelta(seconds=detail['View']['duration'])
            cover = detail['View']['pic']
            title = detail['View']['title']
            owner_uname, owner_uid, owner_face = owner(detail['View']['owner'])
            await self.ui.add_record(Record(segments=[
                User(name=message.data.user_info.uname, uid=message.data.uid, face=message.data.user_info.face),
                PlainText(text=" 点播了 "),
                Anchor(text=f"《{title}》({bvid})", href=f"https://www.bilibili.com/video/{bvid}/"),
                PlainText(text="作者："),
                User(name=owner_uname, uid=owner_uid, face=owner_face),
                # PlainText(text=f"时长：{duration}"),
                PlainText(text="时长：{0}".format(duration)),
            ]))

            target = self.target
            if target is None:
                continue
            write_header = not target.exists()
            with open(target, 'a', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow([
                        'bvid', 'duration', 'title', 'cover',
                        'demander_uname', 'demander_uid', 'demander_face',
                        'owner_uname', 'owner_uid', 'owner_face',
                        'vod_time', 'original_text',
                    ])
                writer.writerow([
                    bvid, duration.total_seconds(), title, cover,
                    message.data.user_info.uname, message.data.uid, message.data.user_info.face,
                    owner_uname, owner_uid, owner_face,
                    message.ct.isoformat(), message.data.message,
                ])
