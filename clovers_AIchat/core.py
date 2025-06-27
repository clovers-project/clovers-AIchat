import httpx
from datetime import datetime
from abc import ABC, abstractmethod
from typing import TypedDict, Literal
from logging import getLogger

logger = getLogger("AICHAT")


class AIChat(ABC):
    """对话模型"""

    def __init__(self) -> None:
        self.running: bool = False
        self.style_prompt: str

    @abstractmethod
    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None: ...

    @abstractmethod
    def memory_clear(self) -> None: ...
    @property
    @abstractmethod
    def name(self) -> str: ...


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


class ChatContext(TypedDict):
    """对话上下文"""

    time: float
    role: Literal["user", "assistant"]
    text: str
    image_url: str | None


class ChatInterface(ChatInfo, AIChat):
    """模型对话接口"""

    messages: list[ChatContext]
    """对话记录"""
    memory: int
    """对话记录长度"""
    timeout: int | float
    """对话超时时间"""
    date: str
    """当前日期"""

    def __init__(self, config: dict, async_client: httpx.AsyncClient) -> None:
        super().__init__()
        self.messages = []
        self.async_client = async_client
        self._parse_config(config)

    @abstractmethod
    def _parse_config(self, config: dict) -> dict: ...
    @abstractmethod
    async def ChatCompletions(self) -> str: ...

    def memory_filter(self, timestamp: int | float):
        """过滤记忆"""
        timeout = timestamp - self.timeout
        self.messages = [message for message in self.messages if message["time"] > timeout]
        if len(self.messages) > self.memory:
            self.messages = self.messages[-self.memory :]
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

    async def chat(self, nickname: str, text: str, image_url: str | None):
        now = datetime.now()
        self.date = f'date:{now.strftime("%Y-%m-%d")}'
        timestamp = now.timestamp()
        chat_context: ChatContext = {
            "time": timestamp,
            "role": "user",
            "text": f'{nickname} [{now.strftime("%H:%M")}] {text}',
            "image_url": image_url,
        }
        self.messages.append(chat_context)
        self.memory_filter(timestamp)
        try:
            resp_content = await self.ChatCompletions()
        except Exception as err:
            del self.messages[-1]
            logger.exception(err)
            return
        self.messages.append({"time": timestamp, "role": "assistant", "text": resp_content, "image_url": None})
        return resp_content

    def memory_clear(self) -> None:
        self.messages.clear()

    @property
    def name(self) -> str:
        return self.model
