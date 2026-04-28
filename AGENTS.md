# AGENTS.md - UBW编码指南

> **重要说明**：本文档所有针对AI助手的回答必须使用**中文**进行说明和代码注释。

## 项目概述

**UBW**（非官方Bilibili魔杖）是一个实时B站直播间弹幕监测和处理系统。它通过WebSocket连接到B站的直播弹幕API，将结构化的Protocol
Buffer消息反序列化为Pydantic模型，并通过可插拔的处理器管道进行处理。

## 架构概述

### 1. **四层架构**

```
CLI层（typer）→ 应用层 → 处理器管道 → 客户端 + 模型系统
```

- **CLI层** (`src/ubw/cli/__init__.py`)：入口点，包含如 `ubw ss`、`ubw p`、`ubw saver` 等命令
- **应用层** (`src/ubw/app/`)：协调多个处理器和客户端的应用程序
- **处理器层** (`src/ubw/handlers/`)：响应事件的处理管道
- **客户端层** (`src/ubw/clients/`)：连接到B站的WebSocket客户端和HTTP客户端
- **模型层** (`src/ubw/models/`)：所有B站消息的Pydantic模型

### 2. **命令模型系统**

UBW反序列化了100多种不同的B站"命令"（消息类型）。每种类型都有一个对应的模型在 `src/ubw/models/blive/` 中（例如：
`danmu_msg.py` 用于评论，`super_chat_message.py` 用于超级留言）。

**关键模式**：模型继承自 `CommandModel`，其中包含一个与B站命令名称匹配的 `cmd` 字段：

```python
class DanmakuCommand(CommandModel):
    cmd = "DANMU_MSG"
    # ... 其他字段
```

适配器验证：`ubw.models.BLIVE_ADAPTER.validate_python(raw_dict) → CommandModel子类`

### 3. **处理器管道设计**

处理器继承自 `BaseHandler` 并实现异步的 `process_one(client, command)` 方法：

- `StrangeStalkerHandler` - 基于正则表达式的聊天过滤
- `DanmakuPHandler` - 具有UI后端的实时显示
- `SaverHandler` - 将原始命令JSON保存到磁盘
- 处理器处理反序列化后的命令，而不是原始JSON

## 关键模式和约定

### **Pydantic模型模式**

#### 额外字段收集（反模式检测）

模型允许 `extra='allow'` 并通过上下文收集未知字段：

```python
# 在 _base.py 中
@model_validator(mode='after')
def warn_extra(self, info: ValidationInfo):
    if self.__pydantic_extra__:
        context = info.context
        if callable(collect_extra := context.get('collect_extra')):
            # 收集额外的未知字段以供调试
            collect_extra((f"{self.__class__.__module__}.{self.__class__.__qualname__}",
                           self.__pydantic_extra__))


# 在处理器中的使用
extras = []
model = ubw.models.BLIVE_ADAPTER.validate_python(command, context={'collect_extra': extras.append})
# extras 现在包含 (模型路径, 未知字段) 元组
```

#### Protocol Buffer + Pydantic集成

通过自定义验证器解码Protocol Buffer字段：

```python
def protobuf_decoder(pb, model_type, *, base64=True):
    """用于Annotated字段以解码base64编码的protobuf"""
    # 解码流程：base64 → protobuf字节 → protobuf消息 → Pydantic模型
    # 示例：Annotated[SubModel, protobuf_decoder(some_pb.SomeMessage, SubModel)]
```

#### 颜色解析（多种格式支持）

模型可以从十六进制、rgba或整数解析颜色：

```python
class Color(RootModel):
    root: tuple[int, int, int] | tuple[int, int, int, int]
    # 支持格式："#AABBCC"、"rgba(170,187,204,255)"、0xAABBCC、(170,187,204)
```

当颜色字段可能为空字符串时，使用 `Color | Literal['']` 以同时支持有效颜色和空字符串。

#### 动态字段别名

对于根据上下文变化的字段，使用 `AliasChoices`：

```python
field_name: str = Field(validation_alias=AliasChoices('name', 'uname', 'user_name'))
```

### **异步编排模式**

`utils.py` 中的 `listen_to_all()` 协调多个直播间和处理器：

- 为每个直播间创建 `WSWebCookieLiveClient` 实例
- 将处理器附加到客户端
- 使用 `await asyncio.gather(client.join() for client in clients)` 进行生命周期管理
- 始终在try/finally中调用 `stop_and_close()` 来清理处理器和客户端

### **配置驱动执行**

TOML配置定义处理器参数；CLI对其进行修补：

```toml
[strange_stalker.elza]
rooms = [81004]
regex = ['pattern']

# CLI 命令：ubw r strange_stalker.elza
# → 加载 config['strange_stalker']['elza']，用这些参数调用命令
```

配置支持通过 `patch_config()` 进行嵌套修补，以及通过 `-D key='value'` 进行CLI覆盖。

### **B站API客户端模式**

针对不同认证场景的多种客户端类型：

- `BilibiliCookieClient` - 使用会话Cookie的HTTP客户端
- `WSWebCookieLiveClient` - 用于实时弹幕的WebSocket客户端
- `BilibiliUnauthorizedClient` - 无需认证的公共API

客户端是异步上下文管理器；始终使用 `async with`。

### **测试模式**

- `tests/ubw/models/test_models.py` 验证命令是否正确反序列化
- **关键测试**：`test_with_history()` 从 `output/unknown_cmd/` 加载原始JSON并验证
    - 确保新的B站消息不会破坏反序列化
    - 模型必须是 `CommandModel` 子类；具体类型根据 `cmd` 字段而异

## 跨组件通信

### **客户端 → 处理器通信**

1. 客户端接收WebSocket帧（用brotli压缩，然后是JSON）
2. 处理器的 `process_one()` 接收反序列化的Pydantic模型
3. 处理器回调 `client.something()`（例如：通过HTTP发送消息）

### **处理器生命周期钩子**

```python
async def start(self, client: LiveClientABC):


# 在客户端初始化后调用

async def join(self):


# 阻塞调用，由asyncio.gather调用
# 使处理器保持活动状态

async def stop_and_close(self):
# 清理资源；在try/finally中调用
```

### **处理器中的错误处理**

- 验证错误被捕获；额外字段被收集（参见上文关键模式）
- 格式错误的命令被记录，不被抛出
- Sentry集成通过config.toml中的 `[sentry]` 部分进行

## 文件组织

- `src/ubw/cli/` - 命令定义（typer）
- `src/ubw/models/blive/` - ~100+个命令模型（从B站协议自动生成）
- `src/ubw/models/bilibili.py` - API响应模型（REST端点）
- `src/ubw/handlers/` - 处理逻辑；一个处理器类型一个文件
- `src/ubw/clients/` - 连接层（WebSocket + HTTP）
- `src/ubw/app/` - 多处理器编排（成为一个有用的应用）
- `output/unknown_cmd/` - 测试数据（来自B站的原始JSON）

## 开发工作流

### **运行处理器**

```bash
poetry run ubw ss <room_id> --regex "pattern"  # 奇异追踪器
poetry run ubw p <room_id>                     # 实时弹幕显示
poetry run ubw s <room_id>                     # 保存命令到JSON
```

### **测试命令反序列化**

```bash
poetry run pytest tests/ubw/models/test_models.py::test_with_history -v
```

### **添加新的命令模型**

1. 阅读 `output/unknown_cmd/` 中的原始JSON以了解新命令的结构
    1. `essentials.json` 代表了过去遇到过的关键未知命令。
    2. `<MODEL_CMD>.json` 代表了自动记录的未知命令实例。
    3. `XX_EXTRA_<full qualified name of Model>.json` 代表了该模型中未定义字段的实例（这严格代表一定只能修改已有模型，不可能新增模型）。
2. 在 `src/ubw/models/blive/<new_command_name>.py` 中创建继承自 `CommandModel` 的模型
    1. 文件开头使用 `from ._base import *` 导入基础工具函数和类
    2. 尝试发现代表颜色的字段并使用 `Color` 模型
    3. 尝试发现代表时间戳的字段并使用 `datetime` 模型
    4. 尽可能使用 3.10+ 的现代Pydantic功能（例如：`field_validator`、`model_validator`、`Annotated`）
    5. 尽可能使用 Python 3.10+ 的现代类型提示（例如：使用 `A|B` 代替 `Union[A,B]`，`list[A]` 代替 `typing.List[A]`）
3. 在 `src/ubw/models/blive/__init__.py` 中
    1. 先 import 对应模型
    2. 将新模型添加到 `AnnotatedCommandModel` 的联合中
    3. 添加到 `__all__` 列表中导出。

### **配置覆盖**

```bash
# 覆盖日志级别以进行调试
poetry run ubw -vv -D 'logging.root.level="DEBUG"' <command>

# 测试应用配置
poetry run ubw app_show <app_name>
poetry run ubw app_run <app_name> -X 'key="value"'
```

## 常见陷阱

1. **额外字段不是错误** - 模型使用 `extra='allow'`，所以未知的B站字段不会导致破坏。这是故意的；额外字段被收集用于调试。
2. **处理器共享状态** - 在多个直播间使用同一处理器实例时，确保线程安全（通常使用异步没有问题，但要注意可变默认值）。
3. **配置修补是浅层的** - `patch_config()` 不进行深度合并数组；使用CLI `-D` 进行精确覆盖。
4. **Pydantic验证器在模型构造前运行** - 对输入转换使用 `BeforeValidator`，对构造后的字段验证使用 `field_validator`。
5. **WebSocket解压是异步的** - brotli解压使用 `asyncio.to_thread()` 来避免阻塞。

## 关键仓库见解

- **B站协议经常变化** - UBW对未知字段放宽验证，而不是因为新字段而破坏
- **命令模型是半自动生成的** - 结构源自B站protobuf规范；自定义验证器手动添加
- **测试预期向后兼容性** - 新命令应该能反序列化而不出错，即使字段是未知的
- **处理器管道是可扩展的** - 添加新处理器不需要修改现有的；只需继承 `BaseHandler`

### **修改现有模型以处理额外字段**

当遇到 `XX_EXTRA_<full qualified name of Model>.json` 文件时，表示该模型有未知字段需要添加：

1. 分析 `output/unknown_cmd/XX_EXTRA_<model_path>.json` 中的未知字段。
2. 在对应的模型文件中添加这些字段，使用适当的类型和默认值（通常为 `str = ""` 或 `int = 0` 等）。
3. 使用 `scripts/try_parse_unknown.py <CMD_NAME>` 验证相关命令的反序列化是否正确。

例如，对于 `XX_EXTRA_ubw.models.blive.anchor_lot.AnchorLotAwardData.json`，添加 `promise_delivery_time: str = ""` 到
`AnchorLotAwardData` 类，然后运行 `poetry run python scripts/try_parse_unknown.py ANCHOR_LOT_AWARD` 以确认修改正确。
