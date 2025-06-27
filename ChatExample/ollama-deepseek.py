from clovers_aichat.core import ChatContext
from clovers_aichat.ai.openai import Chat as OpenAIChat
import re


pattern = re.compile(r"<think>(.*)</think>(.*)", re.DOTALL)


class Chat(OpenAIChat):
    """Ollama DeepSeek"""

    async def ChatCompletions(self):
        def build_content(message: ChatContext):
            return {"role": message["role"], "content": message["text"]}

        messages = []
        messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(map(build_content, self.messages))
        resp = await self.async_client.post(self.url, headers=self.headers, json={"model": self.model, "messages": messages})
        resp.raise_for_status()
        resp_content: str = resp.json()["choices"][0]["message"]["content"].strip()
        matcher = pattern.match(resp_content)
        if matcher is None:
            return resp_content
        else:
            return matcher.group(2).strip()
