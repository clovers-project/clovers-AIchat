from pydantic import BaseModel
from datetime import datetime
from clovers.logger import logger
from .main import Info, Manager
from .openai import Chat as OpenAIChat
from .deepseek import Chat as DeepSeekChat
from .hunyuan import Chat as HunYuanChat
from .gemini import Chat as GeminiChat


def matchChat(key: str):
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
            raise ValueError(f"不支持的模型:{key}")


class Config(Info, BaseModel):
    model: str = ""
    text: dict
    image: dict


class Chat(Manager):
    def __init__(self, config: dict, _name: str = "图文混合模型") -> None:
        super().__init__()
        _config = Config.model_validate(config)
        self.name = _name
        self.whitelist = _config.whitelist
        self.blacklist = _config.blacklist
        ChatText, chat_text_name = matchChat(_config.text["key"])
        ChatImage, chat_image_name = matchChat(_config.image["key"])
        self.chat_text = ChatText(config | _config.text, chat_text_name)
        self.chat_image = ChatImage(config | _config.image, chat_image_name)
        self.model = f"text:{chat_text_name}:{self.chat_text.model} - image:{chat_image_name}:{self.chat_image.model}"

    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
        now = datetime.now()
        timestamp = now.timestamp()
        formated_text = f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}'
        try:
            contect = await self.chat_text.build_content(formated_text, image_url)
        except Exception as err:
            logger.exception(err)
            return
        self.chat_text.messages.append({"time": timestamp, "role": "user", "content": contect})
        self.chat_text.memory_filter(timestamp)
        if image_url:
            self.chat_image.messages.clear()
            try:
                imageChat_contect = await self.chat_image.build_content(formated_text, image_url)
            except Exception as err:
                logger.exception(err)
                return
            self.chat_image.messages.append({"time": 0, "role": "user", "content": imageChat_contect})
            ChatCompletions = self.chat_image.ChatCompletions
        else:
            ChatCompletions = self.chat_text.ChatCompletions
        try:
            resp_content = await ChatCompletions()
            self.chat_text.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
        except Exception as err:
            del self.chat_text.messages[-1]
            logger.exception(err)
            resp_content = None
        return resp_content

    def memory_clear(self) -> None:
        self.chat_text.messages.clear()
