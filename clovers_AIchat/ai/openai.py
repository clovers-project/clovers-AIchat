from pydantic import BaseModel
from ..core import ChatInterface, ChatInfo, ChatContext


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
        self.url = f"{_config.url.rstrip("/")}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {_config.api_key}",
            "Content-Type": "application/json",
        }

    async def ChatCompletions(self):
        def build_content(message: ChatContext):
            text = message["text"]
            image_url = message["image_url"]
            if image_url is None:
                context = text
            else:
                context = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": image_url}}]
            return {"role": message["role"], "content": context}

        messages = []
        messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(map(build_content, self.messages))
        resp = await self.async_client.post(self.url, headers=self.headers, json={"model": self.model, "messages": messages})
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    # async def Responses(self) -> str | None:
    #     def build_content(message: ChatContext):
    #         role = message["role"]
    #         text = message["text"]
    #         image_url = message["image_url"]
    #         if image_url is None:
    #             context = text
    #         elif role == "assistant":
    #             context = [{"type": "output_text", "text": text}, {"type": "output_image", "image_url": image_url}]
    #         else:
    #             context = [{"type": "input_text", "text": text}, {"type": "input_image", "image_url": image_url}]
    #         return {"role": role, "content": context}
