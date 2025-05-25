from pydantic import BaseModel
import base64
from .main import ChatInterface, ChatInfo


class Config(ChatInfo, BaseModel):
    api_key: str


class Chat(ChatInterface):
    """Gemini"""

    def _parse_config(self, config: dict):
        _config = Config.model_validate(config)
        self.model = _config.model
        self.system_prompt = _config.system_prompt
        self.style_prompt = _config.style_prompt
        self.memory = _config.memory
        self.timeout = _config.timeout
        self.url = f"{_config.url.rstrip("/")}/{_config.model}:generateContent?key={_config.api_key}"

    async def build_content(self, text: str, image_url: str | None):
        data: list[dict] = [{"text": text}]
        if image_url:
            response = (await self.async_client.get(image_url)).raise_for_status()
            image_data = base64.b64encode(response.content).decode("utf-8")
            data.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data}})
        return data

    async def ChatCompletions(self):
        data = {
            "system_instruction": {"parts": {"text": self.system_prompt}},
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
