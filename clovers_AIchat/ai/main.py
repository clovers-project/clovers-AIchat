from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
from clovers.core.logger import logger


class Basechat(ABC):
    name: str
    running: bool = False
    model: str
    messages: list[dict]
    whitelist: set[str]
    blacklist: set[str]
    memory: int
    timeout: int | float

    @staticmethod
    @abstractmethod
    def build_content(text: str, image_url: str) -> Any: ...

    @abstractmethod
    async def ChatCompletions(self) -> str | None: ...
    def clear_memory(self):
        """记忆清除"""
        self.messages.clear()

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
        contect = f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}'
        if image_url:
            contect = self.build_content(text, image_url)
        self.messages.append({"time": timestamp, "role": "user", "content": contect})
        self.memory_filter(timestamp)
        try:
            resp_content = await self.ChatCompletions()
            self.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
        except Exception as err:
            del self.messages[-1]
            logger.exception(err)
            resp_content = None
        self.running = False
        return resp_content
