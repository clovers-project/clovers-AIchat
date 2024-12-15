from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from clovers.core.logger import logger


class Info:
    """实例设置"""

    model: str
    """模型版本名"""
    whitelist: set[str] = set()
    """白名单"""
    blacklist: set[str] = set()
    """黑名单"""


class Manager(Info, ABC):
    """实例运行管理类"""

    name: str
    """实例名称"""
    running: bool = False
    """运行同步标签"""

    def __init__(self) -> None:
        self.running = False

    @abstractmethod
    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None: ...


class ChatInfo:
    """对话设置"""

    prompt_system: str
    """系统提示词"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""


class ChatInterface(ChatInfo, Manager):
    """模型对话接口"""

    messages: list[dict]
    """对话记录"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[dict] = []

    @staticmethod
    @abstractmethod
    async def build_content(text: str, image_url: str | None) -> Any: ...

    @abstractmethod
    async def ChatCompletions(self) -> str | None: ...

    def memory_filter(self, timestamp: int | float):
        """过滤记忆"""
        self.messages = self.messages[-self.memory :]
        self.messages = [message for message in self.messages if message["time"] > timestamp - self.timeout]
        if self.messages[0]["role"] == "assistant":
            self.messages = self.messages[1:]
        assert self.messages[0]["role"] == "user"

    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
        now = datetime.now()
        timestamp = now.timestamp()
        try:
            contect = await self.build_content(f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}', image_url)
        except Exception as err:
            logger.exception(err)
            return
        self.messages.append({"time": timestamp, "role": "user", "content": contect})
        self.memory_filter(timestamp)
        try:
            resp_content = await self.ChatCompletions()
            self.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
        except Exception as err:
            del self.messages[-1]
            logger.exception(err)
            return
        return resp_content
