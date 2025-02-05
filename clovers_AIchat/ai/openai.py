from pydantic import BaseModel
import httpx
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from .main import ChatInterface, Info, ChatInfo


class Config(Info, ChatInfo, BaseModel):
    url: str
    api_key: str
    proxy: str | None = None


class Chat(ChatInterface):
    """OpenAI"""

    def __init__(self, config: dict, _name: str = "OpenAI") -> None:
        super().__init__()
        _config = Config.model_validate(config)
        self.name = _name
        self.model = _config.model
        self.prompt_system = _config.prompt_system
        self.whitelist = _config.whitelist
        self.blacklist = _config.blacklist
        self.memory = _config.memory
        self.timeout = _config.timeout
        _url = _config.url
        _api_key = _config.api_key
        _client = httpx.AsyncClient(headers={"Content-Type": "application/json"}, proxy=_config.proxy)
        self.async_client = AsyncOpenAI(api_key=_api_key, base_url=_url, http_client=_client)

    @staticmethod
    async def build_content(text: str, image_url: str | None):
        if image_url:
            return [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        return text

    async def ChatCompletions(self):
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.prompt_system}]
        messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
        resp = await self.async_client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content

    def memory_clear(self) -> None:
        self.messages.clear()
