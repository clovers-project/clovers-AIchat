from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel
from .main import Basechat
from .config import prompt_system


class Config(BaseModel):
    model: str
    url: str
    api_key: str
    whitelist: set[str]
    blacklist: set[str]


def create_Chat(config: dict):
    _config = Config.model_validate(config)
    url = _config.url
    api_key = _config.api_key
    async_client = AsyncOpenAI(api_key=api_key, base_url=url)

    class Chat(Basechat):
        name: str = "通义千问"
        model = _config.model
        whitelist = _config.whitelist
        blacklist = _config.blacklist

        def __init__(self) -> None:
            self.messages: list[dict] = []

        async def ChatCompletions(self):
            messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt_system}]
            messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
            resp = await async_client.chat.completions.create(model=self.model, messages=messages)
            return resp.choices[0].message.content

    return Chat
