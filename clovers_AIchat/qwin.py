from datetime import datetime
from openai import AsyncOpenAI
from .main import Basechat
from .config import config_data

api_key = config_data.qwin_api_key
host = config_data.qwin_host
prompt_system = config_data.prompt_system.format(nickname=config_data.nickname)
timeout = config_data.timeout
model = config_data.qwin_model

async_client = AsyncOpenAI(
    api_key=api_key,
    base_url=host,
)

class Chat(Basechat):
    def __init__(self) -> None:
        self.messages: list[dict] = []
    async def ChatCompletions(self,messages:list[dict]) -> str:
        messages.insert(0,{"role": "system", "content": prompt_system})
        resp = await async_client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return resp.choices[0].message.content

    async def chat(self, nickname: str, content: str):
        now = datetime.now()
        timestamp = now.timestamp()
        self.messages.append(
            {
                "time": timestamp,
                "role": "user",
                "content": f"{nickname}({now.strftime("%Y-%m-%d %H:%M")}):{content}",
            },
        )
        self.messages = self.messages[-20:]
        self.messages = [message for message in self.messages if message["time"] > timestamp - timeout]
        if self.messages[0]["role"] == "assistant":
            self.messages = self.messages[1:]
        assert self.messages[0]["role"] == "user"
        messages = [{"role": message["role"], "content": message["content"]} for message in self.messages]
        try:
            resp = await self.ChatCompletions(messages)
            self.messages.append(
                {
                    "time": timestamp,
                    "role": "assistant",
                    "content": resp,
                },
            )
            return resp
        except Exception as err:
            del self.messages[-1]
            raise err
