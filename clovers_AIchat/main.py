import re
from datetime import datetime
from abc import ABC, abstractmethod
from clovers.core.plugin import Plugin, Result
from clovers.core.logger import logger
from .clovers import Event


plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)


pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")
str_filter = lambda x: pattern.sub("", x)


class Basechat(ABC):
    name: str
    running: bool = False
    model: str
    messages: list[dict]
    whitelist: set[str]
    blacklist: set[str]
    memory: int
    timeout: int | float

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

    async def chat(self, nickname: str, content: str) -> str | None:
        now = datetime.now()
        timestamp = now.timestamp()
        self.messages.append({"time": timestamp, "role": "user", "content": f'{nickname}({now.strftime("%Y-%m-%d %H:%M")}):{content}'})
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

    @classmethod
    def new(cls) -> None:
        def rule(event: Event) -> bool: ...

        if whitelist := cls.whitelist:
            logger.info(f"{cls.name} - {cls.model} 检查规则设置为白名单模式：{whitelist}")
            rule = lambda event: event.to_me and event.group_id in whitelist
        elif blacklist := cls.blacklist:
            logger.info(f"{cls.name} - {cls.model} 检查规则设置为黑名单模式：{blacklist}")
            rule = lambda event: event.to_me and event.group_id not in blacklist
        else:
            logger.info(f"{cls.name} - {cls.model} 未设置黑白名单，已在全部群组启用")
            rule = lambda event: event.to_me

        chats: dict[str, cls] = {}

        @plugin.handle(None, {"group_id", "nickname", "to_me"}, rule=rule, block=False)
        async def _(event: Event):
            group_id = event.group_id
            if group_id not in chats:
                chat = chats[group_id] = cls()
            else:
                chat = chats[group_id]
            content = event.event.raw_command
            if chat.running:
                return
            if content.startswith("记忆清除"):
                chat.clear_memory()
                return "记忆已清除"
            nickname = str_filter(event.nickname) or event.nickname[0]
            return await chat.chat(nickname, content)
