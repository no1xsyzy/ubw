import asyncio
import json
import logging
import ssl as ssl_
import struct

import aiohttp
import brotli

import bilibili
from ._base import *

__all__ = ('WSClient',)

logger = logging.getLogger('wsclient')

DEFAULT_DANMAKU_SERVER_LIST = [
    {'host': 'broadcastlv.chat.bilibili.com', 'port': 2243, 'wss_port': 443, 'ws_port': 2244}
]
HEADER_STRUCT = struct.Struct('>I2H2I')


class WSClient(ClientABC):
    """
    B站直播弹幕客户端，负责连接房间

    :param room_id: URL中的房间ID，可以用短ID
    :param uid: B站用户ID，0表示未登录
    :param session: cookie、连接池
    :param heartbeat_interval: 发送心跳包的间隔时间（秒）
    :param ssl: True表示用默认的SSLContext验证，False表示不验证，也可以传入SSLContext
    """

    def __init__(
            self,
            room_id,
            uid=0,
            session: aiohttp.ClientSession | None = None,
            heartbeat_interval=30,
            ssl: bool | ssl_.SSLContext = True,
    ):
        super().__init__()
        self._tmp_room_id = room_id
        """用来init_room的临时房间ID，可以用短ID"""
        self._uid = uid

        if session is None:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            self._own_session = True
        else:
            self._session = session
            self._own_session = False

        self._heartbeat_interval = heartbeat_interval
        self._ssl = ssl if ssl else ssl_._create_unverified_context()  # noqa

        self._handlers: list[HandlerInterface] = []
        """消息处理器，可动态增删"""

        # 在调用init_room后初始化的字段
        self._room_id = None
        """真实房间ID"""
        self._room_short_id = None
        """房间短ID，没有则为0"""
        self._room_owner_uid = None
        """主播用户ID"""
        self._host_server_list: list[bilibili.Host] | None = None
        """
        弹幕服务器列表
        [{host: "tx-bj4-live-comet-04.chat.bilibili.com", port: 2243, wss_port: 443, ws_port: 2244}, ...]
        """
        self._host_server_token = None
        """连接弹幕服务器用的token"""
        self._buvid3 = None
        """连接弹幕服务器用的 BUVID"""

        # 在运行时初始化的字段
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        """WebSocket连接"""
        self._network_task: asyncio.Task | None = None
        """网络协程 task"""
        self._heartbeat_timer_task: asyncio.Task | None = None
        """发心跳包定时器 task"""

    @property
    def is_running(self) -> bool:
        """
        本客户端正在运行，注意调用stop后还没完全停止也算正在运行
        """
        return self._network_task is not None

    @property
    def room_id(self) -> int | None:
        """
        房间ID，调用init_room后初始化
        """
        return self._room_id

    @property
    def room_short_id(self) -> int | None:
        """
        房间短ID，没有则为0，调用init_room后初始化
        """
        return self._room_short_id

    @property
    def room_owner_uid(self) -> int | None:
        """
        主播用户ID，调用init_room后初始化
        """
        return self._room_owner_uid

    def add_handler(self, handler: HandlerInterface):
        """
        添加消息处理器
        注意多个处理器是并发处理的，不要依赖处理的顺序
        消息处理器和接收消息运行在同一协程，如果处理消息耗时太长会阻塞接收消息，这种情况建议将消息推到队列，让另一个协程处理

        :param handler: 消息处理器
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def remove_handler(self, handler: HandlerInterface):
        """
        移除消息处理器

        :param handler: 消息处理器
        """
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    def start(self):
        """
        启动本客户端
        """
        if self.is_running:
            logger.warning('room=%s client is running, cannot start() again', self.room_id)
            return

        self._network_task = asyncio.create_task(self._network_coroutine_wrapper())

    def stop(self):
        """
        停止本客户端
        """
        if not self.is_running:
            logger.warning('room=%s client is stopped, cannot stop() again', self.room_id)
            return

        self._network_task.cancel()

    async def stop_and_close(self):
        """
        便利函数，停止本客户端并释放本客户端的资源，调用后本客户端将不可用
        """
        if self.is_running:
            self.stop()
            await self.join()
        await self.close()

    async def join(self):
        """
        等待本客户端停止
        """
        if not self.is_running:
            logger.warning('room=%s client is stopped, cannot join()', self.room_id)
            return

        await asyncio.shield(self._network_task)

    async def close(self):
        """
        释放本客户端的资源，调用后本客户端将不可用
        """
        if self.is_running:
            logger.warning('room=%s is calling close(), but client is running', self.room_id)

        # 如果session是自己创建的则关闭session
        if self._own_session:
            await self._session.close()

    async def init_room(self):
        """
        初始化连接房间需要的字段

        :return: True代表没有降级，如果需要降级后还可用，重载这个函数返回True
        """
        res = True
        if not await self._init_room_id_and_owner():
            res = False
        if not await self._init_host_server():
            res = False
        if not await self._init_buvid():
            res = False
        return res

    async def _init_room_id_and_owner(self):
        try:
            info: bilibili.InfoByRoom = await bilibili.get_info_by_room(self._tmp_room_id, session=self._session)
            self._room_id = info.room_info.room_id
            self._room_short_id = info.room_info.short_id
            self._room_owner_uid = info.room_info.uid
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError, bilibili.BilibiliApiError):
            logger.exception('room=%d _init_room_id_and_owner() failed:', self._tmp_room_id)
            self._room_id = self._room_short_id = self._tmp_room_id
            self._room_owner_uid = 0
            return False
        return True

    async def _init_host_server(self):
        try:
            server: bilibili.DanmuInfo = await bilibili.get_danmaku_server(self._room_id)
            self._host_server_list = server.host_list
            self._host_server_token = server.token
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError, bilibili.BilibiliApiError):
            logger.exception('room=%d _init_host_server() failed:', self._room_id)
            self._host_server_list = DEFAULT_DANMAKU_SERVER_LIST
            self._host_server_token = None
            return False
        return True

    async def _init_buvid(self):
        try:
            c: bilibili.FingerSPI = await bilibili.get_finger_spi()
            self._buvid3 = c.b_3
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError, bilibili.BilibiliApiError):
            logger.exception('room=%d _init_buvid() failed:', self._room_id)
            self._buvid3 = None
            return False
        return True

    @staticmethod
    def _make_packet(data: dict, operation: int) -> bytes:
        """
        创建一个要发送给服务器的包

        :param data: 包体JSON数据
        :param operation: 操作码，见Operation
        :return: 整个包的数据
        """
        body = json.dumps(data).encode('utf-8')
        header = HEADER_STRUCT.pack(*HeaderTuple(
            pack_len=HEADER_STRUCT.size + len(body),
            raw_header_size=HEADER_STRUCT.size,
            ver=1,
            operation=operation,
            seq_id=1
        ))
        return header + body

    async def _network_coroutine_wrapper(self):
        """
        负责处理网络协程的异常，网络协程具体逻辑在_network_coroutine里
        """
        try:
            await self._network_coroutine()
        except asyncio.CancelledError:
            # 正常停止
            raise
        except Exception as e:  # noqa
            logger.exception('room=%s _network_coroutine() finished with exception:', self.room_id)
        finally:
            logger.debug('room=%s _network_coroutine() finished', self.room_id)
            self._network_task = None

    async def _network_coroutine(self):
        """
        网络协程，负责连接服务器、接收消息、解包
        """
        # 如果之前未初始化则初始化
        if self._host_server_token is None:
            if not await self.init_room():
                raise InitError('init_room() failed')

        retry_count = 0
        while True:
            try:
                # 连接
                host_server = self._host_server_list[retry_count % len(self._host_server_list)]
                async with self._session.ws_connect(
                        f"wss://{host_server.host}:{host_server.wss_port}/sub",
                        headers={'User-Agent': bilibili.USER_AGENT},
                        receive_timeout=self._heartbeat_interval + 5,
                        ssl=self._ssl
                ) as websocket:
                    self._websocket = websocket
                    await self._on_ws_connect()

                    # 处理消息
                    message: aiohttp.WSMessage
                    async for message in websocket:
                        await self._on_ws_message(message)
                        # 至少成功处理1条消息
                        retry_count = 0

            except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
                # 掉线重连
                pass
            except AuthError:
                # 认证失败了，应该重新获取token再重连
                logger.exception('room=%d auth failed, trying init_room() again', self.room_id)
                if not await self.init_room():
                    raise InitError('init_room() failed')
            except ssl_.SSLError:
                logger.error('room=%d a SSLError happened, cannot reconnect', self.room_id)
                raise
            finally:
                self._websocket = None
                await self._on_ws_close()

            # 准备重连
            retry_count += 1
            logger.warning('room=%d is reconnecting, retry_count=%d', self.room_id, retry_count)
            await asyncio.sleep(1)

    async def _on_ws_connect(self):
        """
        websocket连接成功
        """
        await self._send_auth()
        self._heartbeat_timer_task = asyncio.create_task(self._heartbeat_timer())

    async def _on_ws_close(self):
        """
        websocket连接断开
        """
        if self._heartbeat_timer_task is not None:
            self._heartbeat_timer_task.cancel()
            self._heartbeat_timer_task = None

    async def _send_auth(self):
        """
        发送认证包
        """
        auth_params = {
            'uid': 0,
            'roomid': self._room_id,
            'protover': 3,
            'platform': 'danmuji',
            'type': 2
        }
        if self._host_server_token is not None:
            auth_params['key'] = self._host_server_token
        if self._buvid3 is not None:
            auth_params['buvid'] = self._buvid3

        logger.debug(f"auth_params=%s", auth_params)

        await self._websocket.send_bytes(self._make_packet(auth_params, Operation.AUTH))

    async def _heartbeat_timer(self):
        while True:
            await asyncio.sleep(self._heartbeat_interval)
            if self._websocket is None or self._websocket.closed:
                self._heartbeat_timer_task = None
                return
            asyncio.create_task(self._send_heartbeat())

    async def _send_heartbeat(self):
        """
        发送心跳包
        """
        if self._websocket is None or self._websocket.closed:
            return

        try:
            await self._websocket.send_bytes(self._make_packet({}, Operation.HEARTBEAT))
        except (ConnectionResetError, aiohttp.ClientConnectionError) as e:
            logger.warning('room=%d _send_heartbeat() failed: %r', self.room_id, e)
        except Exception:  # noqa
            logger.exception('room=%d _send_heartbeat() failed:', self.room_id)

    async def _on_ws_message(self, message: aiohttp.WSMessage):
        """
        收到websocket消息

        :param message: websocket消息
        """
        if message.type != aiohttp.WSMsgType.BINARY:
            logger.warning('room=%d unknown websocket message type=%s, data=%s', self.room_id,
                           message.type, message.data)
            return

        try:
            await self._parse_ws_message(message.data)
        except (asyncio.CancelledError, AuthError):
            # 正常停止、认证失败，让外层处理
            raise
        except Exception:  # noqa
            logger.exception('room=%d _parse_ws_message() error:', self.room_id)

    async def _parse_ws_message(self, data: bytes):
        """
        解析websocket消息

        :param data: websocket消息数据
        """
        offset = 0
        try:
            header = HeaderTuple(*HEADER_STRUCT.unpack_from(data, offset))
        except struct.error:
            logger.exception('room=%d parsing header failed, offset=%d, data=%s', self.room_id, offset, data)
            return

        if header.operation in (Operation.SEND_MSG_REPLY, Operation.AUTH_REPLY):
            # 业务消息，可能有多个包一起发，需要分包
            while True:
                body = data[offset + header.raw_header_size: offset + header.pack_len]
                await self._parse_business_message(header, body)

                offset += header.pack_len
                if offset >= len(data):
                    break

                try:
                    header = HeaderTuple(*HEADER_STRUCT.unpack_from(data, offset))
                except struct.error:
                    logger.exception('room=%d parsing header failed, offset=%d, data=%s', self.room_id, offset, data)
                    break

        elif header.operation == Operation.HEARTBEAT_REPLY:
            # 服务器心跳包，前4字节是人气值，后面是客户端发的心跳包内容
            # pack_len不包括客户端发的心跳包内容，不知道是不是服务器BUG
            body = data[offset + header.raw_header_size: offset + header.raw_header_size + 4]
            popularity = int.from_bytes(body, 'big')
            # 自己造个消息当成业务消息处理
            body = {
                'cmd': '_HEARTBEAT',
                'data': {
                    'popularity': popularity
                }
            }
            await self._handle_command(body)

        else:
            # 未知消息
            body = data[offset + header.raw_header_size: offset + header.pack_len]
            logger.warning('room=%d unknown message operation=%d, header=%s, body=%s', self.room_id,
                           header.operation, header, body)

    async def _parse_business_message(self, header: HeaderTuple, body: bytes):
        """
        解析业务消息
        """
        if header.operation == Operation.SEND_MSG_REPLY:
            # 业务消息
            if header.ver == ProtoVer.BROTLI:
                # 压缩过的先解压，为了避免阻塞网络线程，放在其他线程执行
                body = await asyncio.get_running_loop().run_in_executor(None, brotli.decompress, body)
                await self._parse_ws_message(body)
            elif header.ver == ProtoVer.NORMAL:
                # 没压缩过的直接反序列化，因为有万恶的GIL，这里不能并行避免阻塞
                if len(body) != 0:
                    try:
                        body = json.loads(body.decode('utf-8'))
                        await self._handle_command(body)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        logger.error('room=%d, body=%s', self.room_id, body)
                        raise
            else:
                # 未知格式
                logger.warning('room=%d unknown protocol version=%d, header=%s, body=%s', self.room_id,
                               header.ver, header, body)

        elif header.operation == Operation.AUTH_REPLY:
            # 认证响应
            body = json.loads(body.decode('utf-8'))
            if body['code'] != AuthReplyCode.OK:
                raise AuthError(f"auth reply error, code={body['code']}, body={body}")
            await self._websocket.send_bytes(self._make_packet({}, Operation.HEARTBEAT))

        else:
            # 未知消息
            logger.warning('room=%d unknown message operation=%d, header=%s, body=%s', self.room_id,
                           header.operation, header, body)

    async def _handle_command(self, command: dict):
        """
        解析并处理业务消息

        :param command: 业务消息
        """
        # 外部代码可能不能正常处理取消，所以这里加shield
        results = await asyncio.shield(
            asyncio.gather(
                *(handler.handle(self, command) for handler in self._handlers),
                return_exceptions=True
            )
        )
        for res in results:
            if isinstance(res, Exception):
                logger.exception('room=%d _handle_command() failed, command=%s', self.room_id, command, exc_info=res)