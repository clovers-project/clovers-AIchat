import re
from clovers.core.plugin import Plugin, Result
from clovers.core.logger import logger
from collections.abc import Callable
from .clovers import Event
from .config import config_data
from .ai.main import Manager
from .ai.mix import build_Chat as build_MixChat, matchChat


plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)
pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")

type RuleType = Callable[[Event], bool]

permission_check: RuleType = lambda e: e.permission > 0


def new(cls: type[Manager]) -> None:

    if whitelist := cls.whitelist:
        logger.info(f"{cls.name} - {cls.model} 检查规则设置为白名单模式：{whitelist}")
        rule: RuleType = lambda event: event.to_me and event.group_id in whitelist
    elif blacklist := cls.blacklist:
        logger.info(f"{cls.name} - {cls.model} 检查规则设置为黑名单模式：{blacklist}")
        rule: RuleType = lambda event: event.to_me and event.group_id not in blacklist
    else:
        logger.info(f"{cls.name} - {cls.model} 未设置黑白名单，已在全部群组启用")
        rule: RuleType = lambda event: event.to_me

    chats: dict[str, Manager] = {}

    @plugin.handle(["记忆清除"], ["group_id", "to_me", "permission"], rule=[rule, permission_check])
    async def _(event: Event):
        group_id = event.group_id
        if group_id not in chats:
            return
        chat = chats[group_id]
        chat.memory_clear()
        return f"【{chat.name} - {chat.model}】记忆已清除！"

    @plugin.handle(None, ["group_id", "nickname", "to_me", "image_list"], rule=rule, priority=1, block=False)
    async def _(event: Event):
        group_id = event.group_id
        if group_id not in chats:
            chat = chats[group_id] = cls()
        else:
            chat = chats[group_id]
        text = event.event.raw_command
        if chat.running:
            return
        nickname = pattern.sub("", event.nickname) or event.nickname[0]
        chat.running = True
        result = await chat.chat(nickname, text, event.image_url)
        chat.running = False
        return result


config_list = config_data.config_list

for cfg in config_list:
    key: str = cfg["key"]
    _config = {
        "prompt_system": config_data.prompt_system,
        "memory": config_data.memory,
        "timeout": config_data.timeout,
    }
    _config.update(cfg)

    if key == "mix":
        new(build_MixChat(_config))
    else:
        new(matchChat(_config))

__plugin__ = plugin
