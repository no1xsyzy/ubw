import functools
import http.cookies
import logging
import os
from pathlib import Path
from typing import Annotated

import aiofiles
import aiohttp
from multidict import CIMultiDict
from pydantic import Field
from yarl import URL

from ._b_base import *
from .testing import MockBilibiliClient

logger = logging.getLogger('ubw.clients.bilibili')


class BilibiliUnauthorizedClient(BilibiliClientABC):
    auth_type: Literal['no'] = 'no'

    def make_session(self, timeout=None, **kwargs):
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)
        cookie_jar = aiohttp.CookieJar()
        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)
        return aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)


class BilibiliCookieClient(BilibiliClientABC):
    auth_type: Literal['cookie'] = 'cookie'
    cookie_file: Path | None = None

    @functools.cached_property
    def _cookies(self):
        return http.cookies.SimpleCookie()

    async def read_cookie(self, use: Literal['env', 'config', 'default'] = 'default'):
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
                raise NotImplementedError(f"{use=}, expected 'env', 'config' or 'default'")

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

    async def __aenter__(self):
        await self.read_cookie()
        return await super().__aenter__()

    def make_session(self, default_cookies=True, timeout=None, **kwargs):
        headers = CIMultiDict(self.headers)
        headers.setdefault('User-Agent', self.user_agent)

        cookie_jar = aiohttp.CookieJar()
        if default_cookies:
            cookie_jar.update_cookies(self._cookies, URL('https://www.bilibili.com'))

        if timeout is None:
            timeout = aiohttp.ClientTimeout(total=10)

        return aiohttp.ClientSession(headers=headers, cookie_jar=cookie_jar, timeout=timeout, **kwargs)


BilibiliClient = Annotated[
    BilibiliCookieClient | BilibiliUnauthorizedClient | MockBilibiliClient, Field(discriminator='auth_type')]
