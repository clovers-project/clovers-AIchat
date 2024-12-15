from datetime import datetime, timezone
from pydantic import BaseModel
import hashlib
import hmac
import json
import httpx
from .main import ChatInterface, Info, ChatInfo


class Config(Info, ChatInfo, BaseModel):
    url: str
    secret_id: str
    secret_key: str


def headers(
    secret_id: str,
    secret_key: str,
    host: str,
    payload: str,
) -> dict:
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


def build_Chat(config: dict):
    _config = Config.model_validate(config)
    url = _config.url
    host = url.split("//", 1)[1]
    secret_id = _config.secret_id
    secret_key = _config.secret_key
    client = httpx.AsyncClient()

    class Chat(ChatInterface):
        name: str = "腾讯混元"
        model = _config.model
        prompt_system = _config.prompt_system
        whitelist = _config.whitelist
        blacklist = _config.blacklist
        memory = _config.memory
        timeout = _config.timeout

        @staticmethod
        async def build_content(text: str, image_url: str | None):
            return text

        async def ChatCompletions(self):
            messages = [{"Role": "system", "Content": Chat.prompt_system}]
            messages.extend({"Role": message["role"], "Content": message["content"]} for message in self.messages)
            payload = json.dumps({"Model": Chat.model, "Messages": messages}, separators=(",", ":"), ensure_ascii=False)
            resp = await client.post(
                url,
                headers=headers(secret_id=secret_id, secret_key=secret_key, host=host, payload=payload),
                content=payload,
            )
            return resp.json()["Response"]["Choices"][0]["Message"]["Content"]

    return Chat
