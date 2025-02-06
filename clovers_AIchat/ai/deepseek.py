from .openai import Chat as OpenAIChat, ChatCompletionMessageParam


class Chat(OpenAIChat):
    """DeepSeek"""

    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
        if text.endswith("--think"):
            self.think = True
            text = text[:-7].strip()
        else:
            self.think = False
        return await super().chat(nickname, text, image_url)

    @staticmethod
    async def build_content(text: str, image_url: str | None):
        return text

    async def ChatCompletions(self):
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.prompt_system}]
        messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
        resp = await self.async_client.chat.completions.create(model=self.model, messages=messages)
        if self.think:
            reasoning_content: str | None = getattr(resp.choices[0].message, "reasoning_content", None)
            if reasoning_content:
                return f"<think>\n{reasoning_content}\n</think>\n{resp.choices[0].message.content}"
        return resp.choices[0].message.content
