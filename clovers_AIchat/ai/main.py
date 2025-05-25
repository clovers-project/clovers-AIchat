import httpx
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from logging import getLogger

logger = getLogger("AICHAT")


class AIChat(ABC):
    """对话模型"""

    model: str
    """模型版本名"""
    system_prompt: str
    """系统提示词"""
    style_prompt: str
    """风格提示词"""

    def __init__(self) -> None:
        self.running: bool = False

    @abstractmethod
    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None: ...

    @abstractmethod
    def memory_clear(self) -> None: ...


class ChatInfo:
    """对话设置"""

    url: str
    """接入点url"""
    model: str
    """模型版本名"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""
    system_prompt: str
    """系统提示词"""
    style_prompt: str
    """风格提示词"""


class ChatInterface(ChatInfo, AIChat):
    """模型对话接口"""

    messages: list[dict]
    """对话记录"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""
    date: str
    """当前日期"""

    def __init__(self, config: dict, async_client: httpx.AsyncClient) -> None:
        super().__init__()
        self.messages: list[dict] = []
        self.async_client = async_client
        self._parse_config(config)

    @abstractmethod
    def _parse_config(self, config: dict) -> dict: ...

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

    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return f"{self._system_prompt}\n{self.style_prompt}\n{self.date}"

    @system_prompt.setter
    def system_prompt(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt

    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
        now = datetime.now()
        self.date = f'date:{now.strftime("%Y-%m-%d")}'
        try:
            contect = await self.build_content(f'{nickname} [{now.strftime("%H:%M")}] {text}', image_url)
        except Exception as err:
            logger.exception(err)
            return
        timestamp = now.timestamp()
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
