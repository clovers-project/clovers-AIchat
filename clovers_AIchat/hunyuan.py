import json
import hashlib
import hmac
from datetime import datetime, timezone
import httpx
from .main import Basechat
from .config import config_data


secret_id = config_data.hunyuan_secret_id
secret_key = config_data.hunyuan_secret_key
host = config_data.hunyuan_host
prompt_system = config_data.prompt_system.format(nickname=config_data.nickname)
timeout = config_data.timeout


class Chat(Basechat):
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.prompt_start: list[dict] = []
        self.prompt_start.append(
            {
                "Role": "system",
                "Content": prompt_system,
            }
        )
        self.prompt_start.append(
            {
                "Role": "user",
                "Content": "你好",
            },
        )
        self.prompt_start.append(
            {
                "Role": "assistant",
                "Content": "你好，有什么可以帮你的吗？",
            },
        )
        self.client = httpx.AsyncClient()

    @staticmethod
    def headers(payload: str) -> dict:
        algorithm = "TC3-HMAC-SHA256"
        service = "hunyuan"
        version = "2023-09-01"
        action = "ChatCompletions"
        ct = "application/json"
        signed_headers = "content-type;host;x-tc-action"
        now_utc = datetime.now(timezone.utc)
        timestamp = str(int(now_utc.timestamp()))
        date = now_utc.strftime("%Y-%m-%d")
        # 拼接规范请求串
        canonical_request = f"POST\n/\n\ncontent-type:{ct}\nhost:{host}\nx-tc-action:{action.lower()}\n\n{signed_headers}\n{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
        # 拼接待签名字符串
        credential_scope = f"{date}/{service}/tc3_request"
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

        # 计算签名
        def sign(key, msg):
            return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

        secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
        secret_service = sign(secret_date, service)
        secret_signing = sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        # 拼接 Authorization
        return {
            "Authorization": f"{algorithm} Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}",
            "Content-Type": "application/json",
            "Host": host,
            "X-TC-Action": action,
            "X-TC-Timestamp": timestamp,
            "X-TC-Version": version,
        }

    async def ChatCompletions(self, data: dict) -> str:
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        headers = self.headers(payload)
        resp = await self.client.post("https://hunyuan.tencentcloudapi.com", headers=headers, content=payload)
        return resp.json()["Response"]["Choices"][0]["Message"]["Content"]

    async def chat(self, nickname: str, content: str):
        now = datetime.now()
        timestamp = now.timestamp()
        self.messages.append(
            {
                "time": timestamp,
                "Role": "user",
                "Content": f"{nickname}({now.strftime('%Y-%m-%d %H:%M')}):{content}",
            },
        )
        self.messages = self.messages[-20:]
        self.messages = [message for message in self.messages if message["time"] > timestamp - timeout]
        if self.messages[0]["Role"] == "assistant":
            self.messages = self.messages[1:]
        assert self.messages[0]["Role"] == "user"
        messages = self.prompt_start + [{"Role": message["Role"], "Content": message["Content"]} for message in self.messages]
        try:
            resp = await self.ChatCompletions({"Model": "hunyuan-lite", "Messages": messages})
            self.messages.append(
                {
                    "time": timestamp,
                    "Role": "assistant",
                    "Content": resp,
                },
            )
            return resp
        except Exception as err:
            del self.messages[-1]
            raise err
