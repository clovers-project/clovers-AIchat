from pydantic import BaseModel
import httpx
import base64
from .main import ChatInterface, ChatInfo


class Config(ChatInfo, BaseModel):
    api_key: str


class Chat(ChatInterface):
    """Gemini"""

    def __init__(self, config: dict) -> None:
        super().init()
        _config = Config.model_validate(config)
        self.model = _config.model
        self.prompt_system = _config.prompt_system
        self.memory = _config.memory
        self.timeout = _config.timeout
        self.url = f"{_config.url.rstrip("/")}/{_config.model}:generateContent?key={_config.api_key}"
        self.async_client = httpx.AsyncClient(proxy=_config.proxy)

    async def build_content(self, text: str, image_url: str | None):
        data: list[dict] = [{"text": text}]
        if image_url:
            response = (await self.async_client.get(image_url)).raise_for_status()
            image_data = base64.b64encode(response.content).decode("utf-8")
            data.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data}})
        return data

    async def ChatCompletions(self):
        data = {
            "system_instruction": {"parts": {"text": self.prompt_system}},
            "contents": [
                (
                    {
                        "role": "user",
                        "parts": message["content"],
                    }
                    if message["role"] == "user"
                    else {
                        "role": "model",
                        "parts": [{"text": message["content"]}],
                    }
                )
                for message in self.messages
            ],
        }
        resp = (await self.async_client.post(self.url, json=data, headers={"Content-Type": "application/json"})).raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].rstrip("\n")
