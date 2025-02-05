import re
from clovers.plugin import Plugin, Result
from clovers.logger import logger
from collections.abc import Callable
from .clovers import Event
from .config import config_data
from .ai.main import Manager
from .ai.mix import Chat as MixChat, matchChat


plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)
pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")

type RuleType = Callable[[Event], bool]

permission_check: RuleType = lambda e: e.permission > 0


def new(config: dict) -> None:
    key: str = config["key"]
    if key == "mix":
        Chat = MixChat
        name = "图文混合模型"
    else:
        Chat, name = matchChat(key)

    if whitelist := Chat.whitelist:
        logger.info(f"{name} 检查规则设置为白名单模式：{whitelist}")
        rule: RuleType = lambda event: event.to_me and event.group_id in whitelist
    elif blacklist := Chat.blacklist:
        logger.info(f"{name} 检查规则设置为黑名单模式：{blacklist}")
        rule: RuleType = lambda event: event.to_me and event.group_id not in blacklist
    else:
        logger.info(f"{name} 未设置黑白名单，已在全部群组启用")
        rule: RuleType = lambda event: event.to_me

    chats: dict[str, Manager] = {}

    is_command = False

    @plugin.handle(["记忆清除"], ["group_id", "to_me", "permission"], rule=[rule, permission_check], block=False)
    async def _(event: Event):
        nonlocal is_command
        is_command = True
        group_id = event.group_id
        if group_id not in chats:
            return "【AIchat】未找到该群聊的AI对话"
        chat = chats[group_id]
        chat.memory_clear()
        return f"【{chat.name} - {chat.model}】记忆已清除！"

    def chat_rule(event: Event):
        nonlocal is_command
        if is_command:
            is_command = False
            return False
        return rule(event)

    @plugin.handle(None, ["group_id", "nickname", "to_me", "image_list"], rule=chat_rule, priority=1, block=False)
    async def _(event: Event):
        group_id = event.group_id
        if group_id not in chats:
            chat = chats[group_id] = Chat(config, name)
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


for cfg in config_data.config_list:

    _config = {
        "prompt_system": config_data.prompt_system,
        "memory": config_data.memory,
        "timeout": config_data.timeout,
    }
    _config.update(cfg)
    try:
        new(_config)
    except Exception as e:
        logger.exception(e)
        logger.debug(_config)


__plugin__ = plugin
