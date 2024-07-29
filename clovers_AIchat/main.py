import re
from abc import ABC, abstractmethod
from clovers.core.plugin import Plugin, Result
from .clovers import Event
from .config import config_data

BOT_NICKNAME = config_data.nickname

plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)


class Basechat(ABC):
    @abstractmethod
    async def chat(self, nickname: str, content: str) -> str: ...


pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z]")
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
        nickname = str_filter(event.nickname) or event.nickname[:2]
        return await chat.chat(nickname=str_filter(nickname), content=BOT_NICKNAME + event.event.raw_command)
