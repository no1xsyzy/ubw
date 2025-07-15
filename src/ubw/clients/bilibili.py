import functools
import http.cookies
import logging
import os
from pathlib import Path
from typing import Annotated, assert_never

import aiofiles
import aiohttp
from bilibili_api import Credential
from multidict import CIMultiDict
from pydantic import Field
from tinydb import Query
from tinydb.table import Document
from yarl import URL

from ._b_base import *
from .testing import MockBilibiliClient
from ..userdata import tiny_database

logger = logging.getLogger('ubw.clients.bilibili')


class BilibiliUnauthorizedClient(BilibiliClientABC):
    auth_type: Literal['no'] = 'no'

    def make_session(self, timeout=None, **kwargs):
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)
        cookie_jar = aiohttp.CookieJar()
        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)
        client_session = aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)
        logger.debug(f'created aiohttp session with BilibiliUnauthorizedClient {client_session!r}')
        return client_session

    def make_credential(self) -> Credential:
        return Credential()


class BilibiliCookieClient(BilibiliClientABC):
    auth_type: Literal['cookie'] = 'cookie'
    cookie_file: Path | None = None

    _cookie_read: bool = False

    @functools.cached_property
    def _cookies(self):
        return http.cookies.SimpleCookie()

    async def make_credential(self) -> Credential:
        await self._ensure_cookie()
        return Credential(sessdata=self._cookies.get('SESSDATA').value)

    async def _ensure_cookie(self, use: Literal['env', 'config', 'default'] = 'default', force_reread=False):
        if self._cookie_read and not force_reread:
            return

        match use:
            case 'env':
                s = os.environ.get('UBW_COOKIE_FILE')
            case 'config':
                s = self.cookie_file
            case 'default':
                s = os.environ.get('UBW_COOKIE_FILE')
                if s is None:
                    s = self.cookie_file
            case _:
                assert_never(f"{use=}, expected 'env', 'config' or 'default'")

        if s is None:
            raise ValueError('no cookie file provided, use UBW_COOKIE_FILE or config.toml to specify')

        s = Path(s).resolve()
        logger.debug(f"reading cookies from {s}")

        async with aiofiles.open(s, mode='rt', encoding='utf-8') as f:
            async for line in f:
                line = line.strip('\r\n')
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                if not line or line.startswith('#'):
                    continue
                domain, subdomains, path, httponly, expires, name, value = line.split('\t')
                subdomains = subdomains == 'TRUE'
                httponly = httponly == 'TRUE'
                from email.utils import formatdate
                expires = formatdate(int(expires), usegmt=True)
                self._cookies[name] = value
                self._cookies[name]['domain'] = domain
                self._cookies[name]['expires'] = expires
                self._cookies[name]['path'] = path
                self._cookies[name]['httponly'] = httponly
        self._cookie_read = True

    async def make_session(self, *, default_cookies=True, timeout=None, warn_unread_cookie=True, **kwargs):
        await self._ensure_cookie()
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)

        cookie_jar = aiohttp.CookieJar()
        if default_cookies:
            cookie_jar.update_cookies(self._cookies, URL('https://www.bilibili.com'))

        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)

        client_session = aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)
        logger.debug(f'created aiohttp session with BilibiliCookieClient {client_session!r}')
        return client_session


class BilibiliUserdataClient(BilibiliClientABC):
    auth_type: Literal['userdata'] = 'userdata'
    data_entry: str

    _data: dict | None = None

    async def _ensure_data(self):
        if self._data is not None:
            return
        async with tiny_database('users') as db:
            user = Query()
            data = db.get(user.name == self.data_entry)
            if data is None:
                pass  # TODO: login
            assert isinstance(data, Document)
            self._data = dict(data)

    async def make_session(self):
        await self._ensure_data()
        cookie = http.cookies.SimpleCookie()
        for name, key in [('SESSDATA', 'sessdata')]:
            if key in self._data:
                cookie[name] = self._data[key]
                cookie[name]['domain'] = ".bilibili.com"
                cookie[name]['path'] = "/"
                cookie[name]['httponly'] = name == 'SESSDATA'

        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)
        timeout = aiohttp.ClientTimeout(total=10)
        return aiohttp.ClientSession(headers=headers, cookies=cookie, timeout=timeout)

    async def make_credential(self) -> Credential:
        await self._ensure_data()
        Credential.from_cookies(self._data)
        return Credential(**self._data)


BilibiliClient = Annotated[
    BilibiliCookieClient | BilibiliUnauthorizedClient | MockBilibiliClient, Field(discriminator='auth_type')]
