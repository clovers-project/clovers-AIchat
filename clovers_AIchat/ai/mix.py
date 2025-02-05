from datetime import datetime
from clovers.logger import logger
from .main import AIChat, ChatInterface


class Chat(AIChat):
    def __init__(
        self,
        whitelist: set[str],
        blacklist: set[str],
        chat_text: ChatInterface,
        chat_image: ChatInterface,
        model: str = "",
    ) -> None:
        super().__init__()
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.chat_text = chat_text
        self.chat_image = chat_image
        self.model = model

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

    def set_prompt_system(self, prompt_system: str) -> None:
        self.chat_text.prompt_system = prompt_system
