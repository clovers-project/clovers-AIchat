from pydantic import BaseModel


class Config(BaseModel):
    timeout: int = 600
    memory: int = 20
    prompt_system: str = """
你是有着二次元可爱少女形象的AI助手 名为小叶子
以下是你的注意事项
你会在群聊里和不同的群友进行对话
你收到的消息格式为 "昵称 (日期 时间):消息" 例如 "小明 (2024-5-31 12:00):你好" 你的回复不应该有昵称，时间和日期。
你收到的消息含有用户的昵称 你应该注意在与哪个用户对话 不要让昵称的含义影响到你的回复
你会根据当前时间进行相应的寒暄或回应
回答知识问题时 你将保持冷静和专业
回答打趣问题时 你将幽默回复
闲聊时你将简短回复 并在合适时使用颜文字
你不会使用文本标记符号
你的回复要尽可能简短 通常不超过200字 如用户需要问题的详细答案则不要超过600字"""

    config_list: list[dict] = [
        {
            "key": "qwen",
            "model": "qwen-plus",
            "url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": "",
            "whitelist": [],
            "blacklist": [],
        },
        {
            "key": "hunyuan",
            "model": "hunyuan-lite",
            "url": "https://hunyuan.tencentcloudapi.com",
            "secret_id": "",
            "secret_key": "",
            "whitelist": [],
            "blacklist": [],
        },
        {
            "key": "gemini",
            "model": "gemini-1.5-flash",
            "url": "https://generativelanguage.googleapis.com/v1beta/models",
            "api_key": "",
            "whitelist": [],
            "blacklist": [],
        },
        {
            "key": "mix",
            "text": {
                "key": "qwen",
                "model": "qwen-plus",
                "url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
            },
            "image": {
                "key": "qwen",
                "model": "qwen-vl-plus",
                "url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
            },
            "whitelist": [],
            "blacklist": [],
        },
    ]


from clovers.core.config import config as clovers_config

config_key = __package__
config_data = Config.model_validate(clovers_config.get(config_key, {}))
"""主配置类"""
clovers_config[config_key] = config_data.model_dump()
