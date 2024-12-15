from pydantic import BaseModel
import httpx
import base64
from .main import ChatInterface, Info, ChatInfo


class Config(Info, ChatInfo, BaseModel):
    url: str
    api_key: str
    proxies: dict | None = None


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    url = f"{_config.url.rstrip("/")}/{_config.model}:generateContent?key={_config.api_key}"
    client = httpx.AsyncClient(headers={"Content-Type": "application/json"}, proxies=_config.proxies)

    class Chat(ChatInterface):
        name: str = "Gemini"
        model = _config.model
        prompt_system = _config.prompt_system
        whitelist = _config.whitelist
        blacklist = _config.blacklist
        memory = _config.memory
        timeout = _config.timeout

        @staticmethod
        async def build_content(text: str, image_url: str | None):
            data: list[dict] = [{"text": text}]
            if image_url:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode("utf-8")
                data.append({"inline_data": {"mime_type": "image/jpeg", "data": image_data}})
            return data

        async def ChatCompletions(self):
            data = {
                "system_instruction": {"parts": {"text": Chat.prompt_system}},
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
            resp = await client.post(url, json=data)
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    return Chat
