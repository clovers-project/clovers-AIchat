from datetime import datetime, timezone
from pydantic import BaseModel
import hashlib
import hmac
import json
from ..core import ChatInterface, ChatInfo


class Config(ChatInfo, BaseModel):
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


class Chat(ChatInterface):
    """腾讯混元"""

    def _parse_config(self, config: dict):
        _config = Config.model_validate(config)
        self.model = _config.model
        self.system_prompt = _config.system_prompt
        self.style_prompt = _config.style_prompt
        self.memory = _config.memory
        self.timeout = _config.timeout
        self.url = _config.url
        self.host = self.url.split("//", 1)[1]
        self.secret_id = _config.secret_id
        self.secret_key = _config.secret_key

    async def ChatCompletions(self):
        messages = [{"Role": "system", "Content": self.system_prompt}]
        messages.extend({"Role": message["role"], "Content": message["text"]} for message in self.messages)
        payload = {"Model": self.model, "Messages": messages}
        payload = json.dumps({"Model": self.model, "Messages": messages}, separators=(",", ":"), ensure_ascii=False)
        resp = await self.async_client.post(
            self.url,
            headers=headers(secret_id=self.secret_id, secret_key=self.secret_key, host=self.host, payload=payload),
            content=payload,
        )
        resp.raise_for_status()
        return resp.json()["Response"]["Choices"][0]["Message"]["Content"].strip()
