from clovers_AIchat.ai.openai import Chat as OpenAIChat, ChatCompletionMessageParam
from clovers.logger import logger
from datetime import datetime
import re


pattern = re.compile(r"<think>(.*)</think>(.*)", re.DOTALL)


class Chat(OpenAIChat):
    """Ollama DeepSeek"""

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
            messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.system_prompt}]
            messages.extend({"role": message["role"], "content": message["content"]} for message in self.messages)
            resp = await self._client.chat.completions.create(model=self.model, messages=messages)
            resp_content = resp.choices[0].message.content
            if not resp_content:
                return
            matcher = pattern.match(resp_content)
            if not matcher:
                reasoning_content = None
            else:
                reasoning_content, resp_content = matcher.groups()
            resp_content = resp_content.strip()
            self.messages.append({"time": timestamp, "role": "assistant", "content": resp_content})
            if think and reasoning_content:
                return f"<think>\n{reasoning_content}\n</think>\n{resp_content}"
            else:
                return resp_content
        except Exception as err:
            del self.messages[-1]
            logger.exception(err)
            return

    @staticmethod
    async def build_content(text: str, image_url: str | None):
        return text
