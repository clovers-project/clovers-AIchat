from pydantic import BaseModel
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from .main import ChatInterface, ChatInfo


class Config(ChatInfo, BaseModel):
    api_key: str


class Chat(ChatInterface):
    """OpenAI"""

    def _parse_config(self, config: dict) -> None:
        _config = Config.model_validate(config)
        self.model = _config.model
        self.system_prompt = _config.system_prompt
        self.style_prompt = _config.style_prompt
        self.memory = _config.memory
        self.timeout = _config.timeout
        _url = _config.url
        _api_key = _config.api_key
        # _client = httpx.AsyncClient(headers={"Content-Type": "application/json"}, proxy=_config.proxy)
        self._client = AsyncOpenAI(api_key=_api_key, base_url=_url, http_client=self.async_client)

    @staticmethod
    async def build_content(text: str, image_url: str | None):
        if image_url:
            return [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        return text

    async def ChatCompletions(self):
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.system_prompt}]
        messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
        resp = await self._client.chat.completions.create(model=self.model, messages=messages)
        return resp.choices[0].message.content
