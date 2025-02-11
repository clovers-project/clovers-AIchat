from clovers.tools import load_module
from pathlib import Path
from pydantic import BaseModel
from .ai.main import AIChat, ChatInterface
from .ai.mix import Chat as MixChat
from .ai.openai import Chat as OpenAIChat
from .ai.hunyuan import Chat as HunYuanChat
from .ai.gemini import Chat as GeminiChat
from .ai.deepseek import Chat as DeepSeekChat


def matchChat(key: str) -> tuple[type[ChatInterface], str]:
    match key:
        case "chatgpt":
            return OpenAIChat, "ChatGPT"
        case "qwen":
            return OpenAIChat, "通义千问"
        case "deepseek":
            return DeepSeekChat, "DeepSeek"
        case "hunyuan":
            return HunYuanChat, "腾讯混元"
        case "gemini":
            return GeminiChat, "Gemini"
        case _:
            Chat = load_module(".".join(Path(key).relative_to(Path()).parts), "Chat")
            if Chat and isinstance(Chat, type):
                return Chat, key
            raise ValueError(f"不支持的模型:{key}")


class ManagerInfo:
    """实例设置"""

    whitelist: set[str] = set()
    """白名单"""
    blacklist: set[str] = set()
    """黑名单"""


class ManagerConfig(ManagerInfo, BaseModel):
    pass


class MixManagerConfig(ManagerInfo, BaseModel):
    text: dict
    image: dict


class Manager(ManagerInfo):
    """实例运行管理类"""

    name: str
    """实例名称"""

    def __init__(self, config: dict) -> None:
        self.chats: dict[str, AIChat] = {}
        self.config = config
        if config["key"] == "mix":
            self.name = "图文混合模型"
            _config = MixManagerConfig.model_validate(config)
            ChatText, textchatname = matchChat(_config.text["key"])
            chat_text = ChatText(config | _config.text)
            ChatImage, imagechatname = matchChat(_config.image["key"])
            chat_image = ChatImage(config | _config.image)
            model = f"text:{textchatname}:{chat_text.model} - image:{imagechatname}:{chat_image.model}"

            def newChat(config: dict):
                return MixChat(
                    _config.whitelist,
                    _config.blacklist,
                    chat_text,
                    chat_image,
                    model,
                )

            self.newChat = newChat
        else:
            _config = ManagerConfig.model_validate(config)
            self.newChat, self.name = matchChat(config["key"])
        self.whitelist = _config.whitelist
        self.blacklist = _config.blacklist

    def chat(self, group_id: str):
        if group_id not in self.chats:
            self.chats[group_id] = self.newChat(self.config)
        return self.chats[group_id]
