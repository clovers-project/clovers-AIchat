from pydantic import BaseModel
import httpx
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from .main import ChatInterface, Info, ChatInfo


class Config(Info, ChatInfo, BaseModel):
    url: str
    api_key: str
    proxy: str | None = None


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    _url = _config.url
    _api_key = _config.api_key
    _client = httpx.AsyncClient(headers={"Content-Type": "application/json"}, proxy=_config.proxy)
    async_client = AsyncOpenAI(api_key=_api_key, base_url=_url, http_client=_client)

    class Chat(ChatInterface):
        name = "DeepSeek"
        model = _config.model
        prompt_system = _config.prompt_system
        whitelist = _config.whitelist
        blacklist = _config.blacklist
        memory = _config.memory
        timeout = _config.timeout
        think = False

        @staticmethod
        async def build_content(text: str, image_url: str | None):
            if image_url:
                return [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            return text

        async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
            if text.endswith("--think"):
                self.think = True
                text = text[:-7].strip()
            else:
                self.think = False
            return await super().chat(nickname, text, image_url)

        async def ChatCompletions(self):
            messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": Chat.prompt_system}]
            messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
            resp = await async_client.chat.completions.create(model=Chat.model, messages=messages)
            if self.think:
                reasoning_content: str | None = getattr(resp.choices[0].message, "reasoning_content", None)
                if reasoning_content:
                    return f"<think>\n{reasoning_content}\n</think>\n{resp.choices[0].message.content}"
                else:
                    return resp.choices[0].message.content
            else:
                return resp.choices[0].message.content

        def memory_clear(self) -> None:
            self.messages.clear()

    return Chat
