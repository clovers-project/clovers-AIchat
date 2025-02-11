from datetime import datetime
from clovers.logger import logger
from .openai import Chat as OpenAIChat, ChatCompletionMessageParam


class Chat(OpenAIChat):
    """DeepSeek"""

    async def chat(self, nickname: str, text: str, image_url: str | None) -> str | None:
        if text.endswith("--think"):
            think = True
            text = text[:-7].strip()
        else:
            think = False
        now = datetime.now()
        timestamp = now.timestamp()
        try:
            contect = await self.build_content(f'{nickname} ({now.strftime("%Y-%m-%d %H:%M")}):{text}', image_url)
        except Exception as err:
            logger.exception(err)
            return
        self.messages.append({"time": timestamp, "role": "user", "content": contect})
        self.memory_filter(timestamp)
        try:
            messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.prompt_system}]
            messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
            resp = await self.async_client.chat.completions.create(model=self.model, messages=messages)
            resp_content = resp.choices[0].message.content
            self.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
            if think:
                reasoning_content: str | None = getattr(resp.choices[0].message, "reasoning_content", None)
                if reasoning_content:
                    return f"<think>\n{reasoning_content}\n</think>\n{resp_content}"
            return resp_content
        except Exception as err:
            del self.messages[-1]
            logger.exception(err)
            return

    @staticmethod
    async def build_content(text: str, image_url: str | None):
        return text
