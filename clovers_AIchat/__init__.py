import re
from clovers.plugin import Plugin, Result
from clovers.logger import logger
from collections.abc import Callable
from .clovers import Event
from .config import config_data
from .manager import Manager


plugin = Plugin(
    build_event=lambda event: Event(event),
    build_result=lambda result: Result("text", result),
    priority=100,
)
pattern = re.compile(r"[^\u4e00-\u9fa5a-zA-Z\s]")

type RuleType = Callable[[Event], bool]

permission_check: RuleType = lambda e: e.permission > 0


def new(config: dict) -> None:
    chat_manager = Manager(config)
    if whitelist := chat_manager.whitelist:
        logger.info(f"{chat_manager.name} 检查规则设置为白名单模式：{whitelist}")
        rule: RuleType = lambda event: event.to_me and event.group_id in whitelist
    elif blacklist := chat_manager.blacklist:
        logger.info(f"{chat_manager.name} 检查规则设置为黑名单模式：{blacklist}")
        rule: RuleType = lambda event: event.to_me and event.group_id not in blacklist
    else:
        logger.info(f"{chat_manager.name} 未设置黑白名单，已在全部群组启用")
        rule: RuleType = lambda event: event.to_me

    is_command = False

    @plugin.handle(["记忆清除"], ["group_id", "to_me", "permission"], rule=[rule, permission_check], block=False)
    async def _(event: Event):
        nonlocal is_command
        is_command = True
        chat = chat_manager.chat(event.group_id)
        chat.memory_clear()
        return f"本群【{chat_manager.name} - {chat.model}】记忆已清除！"

    @plugin.handle(["修改设定"], ["group_id", "to_me", "permission"], rule=[rule, permission_check], block=False)
    async def _(event: Event):
        nonlocal is_command
        is_command = True
        prompt_system = event.event.raw_command[4:]
        chat = chat_manager.chat(event.group_id)
        if prompt_system:
            chat.memory_clear()
            chat.set_prompt_system(
                prompt_system
                + '\n你收到的消息格式为 "昵称 (日期 时间):消息" 例如 "小明 (2024-5-31 12:00):你好" 你的回复不应该有昵称，时间和日期。'
                "\n你收到的消息含有用户的昵称 你应该注意在与哪个用户对话 不要让昵称的含义影响到你的回复"
            )
            return f"本群【{chat_manager.name} - {chat.model}】设定已修改！"
        else:
            del chat_manager.chats[event.group_id]
            return f"本群【{chat_manager.name} - {chat.model}】设定已重置！"

    def chat_rule(event: Event):
        nonlocal is_command
        if is_command:
            is_command = False
            return False
        return rule(event)

    @plugin.handle(None, ["group_id", "nickname", "to_me", "image_list"], rule=chat_rule, priority=1, block=False)
    async def _(event: Event):
        chat = chat_manager.chat(event.group_id)
        if chat.running:
            return
        text = event.event.raw_command
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
