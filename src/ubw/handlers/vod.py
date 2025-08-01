import re
from datetime import timedelta
from operator import itemgetter

from bilibili_api.video import Video

from ._base import *
from ..clients import LiveClientABC, BilibiliClient
from ..ui.stream_view import StreamView, Richy, Record, User, PlainText, Anchor

owner = itemgetter('name', 'mid', 'face')


class VodHandler(BaseHandler):
    cls: Literal['vod'] = 'vod'

    # DI
    ui: StreamView = Richy()
    owned_ui: bool = True

    async def on_super_chat_message(self, client: LiveClientABC, message: models.SuperChatCommand):
        bclient: BilibiliClient = client.bilibili_client
        for bvid in re.findall(r"BV\w{10}", message.data.message):
            detail = await Video(bvid, await bclient.get_credential()).get_detail()
            duration = timedelta(seconds=detail['View']['duration'])
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
