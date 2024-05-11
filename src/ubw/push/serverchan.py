import logging
from functools import cached_property

import aiohttp
from pydantic import BaseModel

logger = logging.getLogger('serverchan')


class ServerChanMessage(BaseModel):
    """
    :var title: 消息标题，必填。最大长度为 32 。
    :var desp: 消息内容，选填。支持 Markdown语法 ，最大长度为 32KB ,消息卡片截取前 30 显示。
    :var short: 消息卡片内容，选填。最大长度64。如果不指定，将自动从desp中截取生成。
    :var noip: 是否隐藏调用IP，选填。如果不指定，则显示；为1则隐藏。
    :var channel: 动态指定本次推送使用的消息通道，选填。如不指定，则使用网站上的消息通道页面设置的通道。支持最多两个通道，多个通道值用竖线|隔开。比如，同时发送服务号和企业微信应用消息通道，则使用 9|66 。通道对应的值如下：
        方糖服务号=9
        企业微信应用消息=66
        Bark iOS=8
        企业微信群机器人=1
        钉钉群机器人=2
        飞书群机器人=3
        测试号=0
        自定义=88
        PushDeer=18
        官方Android版·β=98
    :var openid: 消息抄送的openid，选填。只支持测试号和企业微信应用消息通道。测试号的 openid 从测试号页面获得 ，多个 openid 用 , 隔开。企业微信应用消息通道的 openid 参数，内容为接收人在企业微信中的 UID（可在消息通道页面配置好该通道后通过链接查看） , 多个人请 | 隔开，即可发给特定人/多个人。不填则发送给通道配置页面的接收人。
    """
    title: str
    desp: str
    short: str | None = None
    noip: int | None = None
    channel: str | None = None
    openid: str | None = None


class ServerChanPusher(BaseModel):
    key: str

    @cached_property
    def session(self):
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        logger.debug(f'created aiohttp session by ServerChanPusher {session!r}')
        return session

    async def push(self, content: ServerChanMessage):
        postdata = aiohttp.FormData(content.model_dump(mode='json', exclude_defaults=True))
        try:
            async with self.session.post(f"https://sctapi.ftqq.com/{self.key}.send", data=postdata) as resp:
                if resp.status == 200:
                    logger.debug("server chan response %s", await resp.text())
                else:
                    logger.info("server chan response %s", await resp.text())
        except Exception as e:
            logger.exception('server chan error', exc_info=e)
