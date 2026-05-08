import csv
import json
import logging
import re
import warnings
from datetime import timedelta, datetime
from functools import cached_property
from operator import itemgetter
from pathlib import Path
from typing import IO, ContextManager, AsyncContextManager

from bilibili_api import ApiException
from bilibili_api.video import Video

from ubw.clients import LiveClientABC, BilibiliClient
from ubw.models.blive.super_chat_message import SuperChatCommand
from ubw.ui.stream_view import StreamView, Richy, Record, User, PlainText, Anchor
from .._base import *

owner = itemgetter('name', 'mid', 'face')

_LOG = logging.getLogger('ubw.handlers.vod')


class MultiContextMixin(BaseHandler):  # TODO: maybe move to _base
    @cached_property
    def __cms(self) -> list[tuple[Literal['a'], AsyncContextManager] | tuple[Literal['s'], ContextManager]]:
        return []

    async def awith(self, acm: AsyncContextManager):
        self.__cms.append(('a', acm))
        return await acm.__aenter__()

    def with_(self, cm: ContextManager):
        self.__cms.append(('s', cm))
        return cm.__enter__()

    async def close(self):
        try:
            while True:
                match self.__cms.pop():
                    case ['a', acm]:
                        acm: AsyncContextManager
                        await acm.__aexit__(None, None, None)
                    case ['s', cm]:
                        cm: ContextManager
                        cm.__exit__(None, None, None)
        except IndexError:
            pass
        await super().close()


class VodHandler(MultiContextMixin, BaseHandler):
    cls: Literal['vod'] = 'vod'

    save_csv: str | None = None
    save_jsonl: str | None = None

    # DI
    ui: StreamView = Richy()
    owned_ui: bool = True

    async def stop(self):
        if self.owned_ui:
            await self.ui.stop()

    @classmethod
    def format_path(cls, strpath: str) -> Path:
        if "{date}" in strpath:
            strpath = strpath.replace("{date}", datetime.today().strftime("%Y%m%d"))
        path = Path(strpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @cached_property
    def csv_writer(self) -> csv.DictWriter | None:
        if self.save_csv is None:
            return None
        path = self.format_path(self.save_csv)
        write_header = not path.exists() or path.stat().st_size == 0
        f = self.with_(open(path, 'a', encoding='utf-8', newline=''))
        writer = csv.DictWriter(f, [
            # demand info
            'demander_uname', 'demander_uid', 'demander_face',
            'vod_time', 'original_text', 'price',
            'bvid',
            # video info
            'duration', 'title', 'cover',
            'owner_uname', 'owner_uid', 'owner_face',
            'tags',
        ])
        if write_header:
            writer.writeheader()
        return writer

    @cached_property
    def jsonl_file(self) -> IO[str] | None:
        if self.save_jsonl is None:
            return None
        path = self.format_path(self.save_jsonl)
        f = self.with_(open(path, 'a', encoding='utf-8'))
        return f

    async def on_super_chat_message(self, client: LiveClientABC, message: SuperChatCommand):
        bclient: BilibiliClient = client.bilibili_client
        demander_uname = message.data.user_info.uname
        demander_uid = message.data.uid
        demander_face = message.data.user_info.face
        original_text = message.data.message
        vod_time = message.ct.isoformat()
        price = message.data.price
        for mat in re.finditer(r"BV\w{,10}", original_text):
            warning = None
            bvid = mat.group(0)
            if len(bvid) != 12:
                warnings.warn(warning := f"{bvid=}长度不足12，可能无法获取信息")
            elif set(bvid) - set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'):
                warnings.warn(warning := f"{bvid=}不是有效的 base58，可能无法获取信息")
            done_csv = False
            done_jsonl = False
            try:
                detail = await Video(bvid, credential=await bclient.get_credential()).get_detail()
                duration = timedelta(seconds=detail['View']['duration'])
                cover = detail['View']['pic']
                title = detail['View']['title']
                print(f"{detail.keys()=}")
                tags = [f"#{tag_info['tag_name']}#" if tag_info['tag_type'] == 'topic' else tag_info['tag_name']
                        for tag_info in detail['Tags']]
                owner_uname, owner_uid, owner_face = owner(detail['View']['owner'])
                await self.ui.add_record(Record(segments=[
                    User(name=demander_uname, uid=demander_uid, face=demander_face),
                    PlainText(text=" 点播了 "),
                    Anchor(text=f"《{title}》({bvid})", href=f"https://www.bilibili.com/video/{bvid}/"),
                    PlainText(text="作者："),
                    User(name=owner_uname, uid=owner_uid, face=owner_face),
                    PlainText(text="时长：{0}".format(duration)),
                ]))

                jsonf = self.jsonl_file
                if jsonf is not None:
                    json.dump({
                        'bvid': bvid,
                        'duration': duration.total_seconds(),
                        'title': title,
                        'cover': cover,
                        'demander_uname': demander_uname,
                        'demander_uid': demander_uid,
                        'demander_face': demander_face,
                        'owner_uname': owner_uname,
                        'owner_uid': owner_uid,
                        'owner_face': owner_face,
                        'vod_time': vod_time,
                        'original_text': original_text,
                        'price': (price),
                        'tags': tags,
                    }, jsonf, ensure_ascii=True)
                    jsonf.write('\n')
                    jsonf.flush()
                done_jsonl = True

                csv_writer = self.csv_writer
                if csv_writer is not None:
                    csv_writer.writerow({
                        'bvid': bvid,
                        'duration': duration.total_seconds(),
                        'title': title,
                        'cover': cover,
                        'demander_uname': demander_uname,
                        'demander_uid': demander_uid,
                        'demander_face': demander_face,
                        'owner_uname': owner_uname,
                        'owner_uid': owner_uid,
                        'owner_face': owner_face,
                        'vod_time': vod_time,
                        'original_text': original_text,
                        'price': price,
                        'tags': '|'.join(tags),
                    })
                done_csv = True
            except ApiException as e:
                _LOG.error(warning := f"获取{bvid=}视频信息出错：{e.msg}")
            except Exception as e:
                _LOG.error(warning := f"{bvid=}出错，{e}")

            # 尝试拯救一些信息，避免真丢失
            if not done_jsonl:
                jsonf = self.jsonl_file
                if jsonf is not None:
                    json.dump({
                        '_broken': True,
                        'bvid': bvid,
                        'demander_uname': demander_uname,
                        'demander_uid': demander_uid,
                        'demander_face': demander_face,
                        'vod_time': vod_time,
                        'original_text': original_text,
                        'price': price,
                        'warning': warning,
                    }, jsonf, ensure_ascii=True)
                    jsonf.write('\n')
                    jsonf.flush()
            if not done_csv:
                csv_writer = self.csv_writer
                if csv_writer is not None:
                    csv_writer.writerow({
                        'bvid': bvid,
                        'demander_uname': demander_uname,
                        'demander_uid': demander_uid,
                        'demander_face': demander_face,
                        'vod_time': vod_time,
                        'original_text': original_text,
                        'price': price,
                        'warning': warning,
                        'duration': '_broken',
                    })
