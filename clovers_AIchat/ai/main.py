from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from clovers.logger import logger


class AIChat(ABC):
    """对话模型"""

    model: str
    """模型版本名"""

    def __init__(self) -> None:
        self.running: bool = False

    @abstractmethod
    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None: ...

    @abstractmethod
    def memory_clear(self) -> None: ...

    @abstractmethod
    def set_prompt_system(self, prompt_system: str) -> None: ...


class ChatInfo:
    """对话设置"""

    url: str
    """接入点url"""
    model: str
    """模型版本名"""
    prompt_system: str
    """系统提示词"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""
    proxy: str | None = None
    """代理地址"""


class ChatInterface(ChatInfo, AIChat):
    """模型对话接口"""

    messages: list[dict]
    """对话记录"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""

    def init(self) -> None:
        super().__init__()
        self.messages: list[dict] = []

    @abstractmethod
    def __init__(self, config: dict) -> None: ...

    @abstractmethod
    async def build_content(self, text: str, image_url: str | None) -> Any: ...

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

    def memory_clear(self) -> None:
        self.messages.clear()

    def set_prompt_system(self, prompt_system: str) -> None:
        self.prompt_system = prompt_system
