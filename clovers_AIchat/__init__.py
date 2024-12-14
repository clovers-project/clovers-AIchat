import re
from clovers.core.plugin import Plugin, Result
from clovers.core.logger import logger
from .clovers import Event
from .config import config_data
from .ai.main import Basechat
from .ai.qwin import build_Chat as build_QwinChat
from .ai.hunyuan import build_Chat as build_HunYuanChat

plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)
pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")


def new(cls: type[Basechat]) -> None:
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

    chats: dict[str, Basechat] = {}

    @plugin.handle(None, {"group_id", "nickname", "to_me", "image_list"}, rule=rule, block=False)
    async def _(event: Event):
        group_id = event.group_id
        if group_id not in chats:
            chat = chats[group_id] = cls()
        else:
            chat = chats[group_id]
        text = event.event.raw_command
        if chat.running:
            return
        if text.startswith("记忆清除"):
            chat.clear_memory()
            return "记忆已清除"
        nickname = pattern.sub("", event.nickname) or event.nickname[0]
        return await chat.chat(nickname, text, event.image_url)


config_list = config_data.config_list

for cfg in config_list:
    key: str = cfg["key"]
    _config = {
        "prompt_system": config_data.prompt_system,
        "memory": config_data.memory,
        "timeout": config_data.timeout,
    }
    _config.update(cfg)

    match key:
        case "qwin":
            new(build_QwinChat(_config))
        case "qwin-lv":
            new(build_QwinChat(_config))
        case "hunyuan":
            new(build_HunYuanChat(_config))
        case _:
            raise ValueError(f"Invalid config key {key}")


__plugin__ = plugin
