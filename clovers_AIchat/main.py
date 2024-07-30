import re
from abc import ABC, abstractmethod
from clovers.core.plugin import Plugin, Result
from clovers.core.logger import logger
from .clovers import Event
from .config import config_data

BOT_NICKNAME = config_data.nickname

plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)


class Basechat(ABC):
    running: bool = False
    model: str
    messages: list[dict]

    @abstractmethod
    async def chat(self, nickname: str, content: str) -> str: ...

    async def sync_chat(self, **kwargs) -> str:
        self.running = True
        try:
            result = await self.chat(**kwargs)
        except Exception as err:
            logger.exception(err)
            result = None
        self.running = False
        return result

    def clear_memory(self):
        """记忆清除"""
        self.messages.clear()


pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")
str_filter = lambda x: pattern.sub("", x)


def create_chat(whitegroups: set[str], blackgroups: set[str], Chat: type[Basechat]) -> None:
    def rule(event: Event) -> bool: ...

    if whitegroups:
        rule = lambda event: event.to_me and event.group_id in whitegroups
    elif blackgroups:
        rule = lambda event: event.to_me and event.group_id not in blackgroups
    else:
        rule = lambda event: event.to_me

    chats: dict[str, Chat] = {}

    @plugin.handle(None, {"group_id", "nickname", "to_me"}, rule=rule)
    async def _(event: Event):
        group_id = event.group_id
        if group_id not in chats:
            chat = chats[group_id] = Chat()
        else:
            chat = chats[group_id]

        content = event.event.raw_command

        if content.startswith("记忆清除"):
            chat.clear_memory()
            return "记忆已清除"

        if chat.running:
            return

        nickname = str_filter(event.nickname) or event.nickname[:2]
        if not content.startswith(BOT_NICKNAME):
            content = BOT_NICKNAME + content
        return await chat.sync_chat(nickname=str_filter(nickname), content=content)
