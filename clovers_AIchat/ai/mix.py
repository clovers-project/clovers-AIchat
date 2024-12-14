from pydantic import BaseModel
from datetime import datetime
from clovers.core.logger import logger
from .main import ChatManager
from .qwin import build_Chat as build_QwinChat
from .hunyuan import build_Chat as build_HunYuanChat


def matchChat(config: dict):
    key = config["key"]
    match key:
        case "qwen":
            return build_QwinChat(config)
        case "hunyuan":
            return build_HunYuanChat(config)
        case _:
            raise ValueError(f"不支持的AI类型:{key}")


class Config(BaseModel):
    text: dict
    image: dict
    whitelist: set[str] = set()
    blacklist: set[str] = set()
    prompt_system: str
    memory: int
    timeout: int | float


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    text_config = _config.text
    image_config = _config.image
    textChat = matchChat(config | text_config)
    imageChat = matchChat(config | image_config)

    class Chat(ChatManager):
        name: str = "图文混合模型"
        model = f'text:{text_config["key"]} - image:{image_config["key"]}'
        whitelist = _config.whitelist
        blacklist = _config.blacklist
        memory = _config.memory - 1
        timeout = _config.timeout

        def __init__(self) -> None:
            self.textChat = textChat()
            self.imageChat = imageChat()

        async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
            now = datetime.now()
            timestamp = now.timestamp()
            formated_text = f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}'
            self.textChat.messages.append({"time": timestamp, "role": "user", "content": formated_text})
            self.textChat.memory_filter(timestamp)
            if image_url:
                contect = self.imageChat.build_content(text, image_url)
                self.imageChat.messages.append({"time": 0, "role": "user", "content": contect})
                ChatCompletions = self.imageChat.ChatCompletions
            else:
                ChatCompletions = self.textChat.ChatCompletions
            try:
                resp_content = await ChatCompletions()
                self.textChat.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
            except Exception as err:
                del self.textChat.messages[-1]
                logger.exception(err)
                resp_content = None
            self.running = False
            return resp_content

    return Chat
