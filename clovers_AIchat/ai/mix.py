from pydantic import BaseModel
from datetime import datetime
from clovers.logger import logger
from .main import Info, Manager
from .openai import build_Chat as build_OpenAIChat
from .deepseek import build_Chat as build_DeepSeekChat
from .hunyuan import build_Chat as build_HunYuanChat
from .gemini import build_Chat as build_GeminiChat


def matchChat(config: dict):
    key = config["key"]
    match key:
        case "chatgpt":
            return build_OpenAIChat(config, "ChatGPT")
        case "qwen":
            return build_OpenAIChat(config, "通义千问")
        case "deepseek":
            return build_DeepSeekChat(config)
        case "hunyuan":
            return build_HunYuanChat(config)
        case "gemini":
            return build_GeminiChat(config)
        case _:
            logger.error(f"不支持的AI类型:{key}，配置信息已忽略")
            logger.debug(config)


class Config(Info, BaseModel):
    model: str = ""
    text: dict
    image: dict


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    textChat = matchChat(config | _config.text)
    imageChat = matchChat(config | _config.image)

    if not textChat or not imageChat:
        return

    class Chat(Manager):
        name: str = "图文混合模型"
        model = f"text:{textChat.model} - image:{imageChat.model}"
        whitelist = _config.whitelist
        blacklist = _config.blacklist

        def __init__(self) -> None:
            self.textChat = textChat()
            self.imageChat = imageChat()

        async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
            now = datetime.now()
            timestamp = now.timestamp()
            formated_text = f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}'
            try:
                contect = await self.textChat.build_content(formated_text, image_url)
            except Exception as err:
                logger.exception(err)
                return
            self.textChat.messages.append({"time": timestamp, "role": "user", "content": contect})
            self.textChat.memory_filter(timestamp)
            if image_url:
                self.imageChat.messages.clear()
                try:
                    imageChat_contect = await self.imageChat.build_content(formated_text, image_url)
                except Exception as err:
                    logger.exception(err)
                    return
                self.imageChat.messages.append({"time": 0, "role": "user", "content": imageChat_contect})
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
            return resp_content

        def memory_clear(self) -> None:
            self.textChat.messages.clear()

    return Chat
