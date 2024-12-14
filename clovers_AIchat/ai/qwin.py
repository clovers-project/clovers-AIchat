from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel
from .main import ChatInterface, ChatManager


class Config(BaseModel):
    model: str
    url: str
    api_key: str
    whitelist: set[str] = set()
    blacklist: set[str] = set()
    prompt_system: str
    memory: int
    timeout: int | float


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    url = _config.url
    api_key = _config.api_key
    async_client = AsyncOpenAI(api_key=api_key, base_url=url)
    prompt_system = _config.prompt_system

    class Chat(ChatInterface, ChatManager):
        name: str = "通义千问"
        model = _config.model
        whitelist = _config.whitelist
        blacklist = _config.blacklist
        memory = _config.memory
        timeout = _config.timeout

        @staticmethod
        def build_content(text: str, image_url: str):
            return [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]

        async def ChatCompletions(self):
            messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt_system}]
            messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
            resp = await async_client.chat.completions.create(model=self.model, messages=messages)
            return resp.choices[0].message.content

    return Chat
