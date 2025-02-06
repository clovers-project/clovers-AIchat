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
        if image_url:
            now = datetime.now()
            timestamp = now.timestamp()
            try:
                contect = await self.chat_text.build_content(f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}', None)
            except Exception as err:
                logger.exception(err)
                return
            self.chat_image.memory_clear()
            resp_content = await self.chat_image.chat(nickname, text, image_url)
            self.chat_text.messages.append({"time": timestamp, "role": "user", "content": contect})
            self.chat_text.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
        else:
            resp_content = await self.chat_text.chat(nickname, text, image_url)
        return resp_content

    def memory_clear(self) -> None:
        self.chat_text.messages.clear()

    def set_prompt_system(self, prompt_system: str) -> None:
        self.chat_text.prompt_system = prompt_system
