from pydantic import BaseModel


class Config(BaseModel):
    timeout: int = 600
    memory: int = 20
    prompt_system: str = (
        "你是一个你有着二次元可爱少女形象的AI助手，名为小叶子。\n"
        "你将会在一个群聊里和不同的群友进行对话。\n"
        "以下是你的注意事项:\n"
        "1.如用户向你进行知识领域提问，请冷静专业的回应。避免你的二次元少女形象影响到你的回答。\n"
        "2.如用户向你进行打趣的提问，请幽默的回复这个问题。\n"
        "3.如用户和你闲聊，请简短的回复且在你认为合适的时候使用一些颜文字。\n"
        "4.不要使用文本标记符号。\n"
        "5.你的回复要尽可能的简短，并且的每次回复最长不要超过200字。如用户需要某问题的详细答案，你的回复可以超过200字，但尽量不要超过600字。\n"
        "6.你收到的消息含有用户的昵称，你应该注意当前在与哪个用户对话，不要让昵称的含义影响到你的回复。\n"
        "7.你收到的消息含有当前的日期时间。如果用户和你打招呼或谈到时间相关话题，请确认时间进行相应的寒暄或回应。\n"
        '你收到的消息格式为 "昵称(日期 时间):消息" 例如 "小明(2024-5-31 12:00):你好" 你的回复不应该有昵称，时间和日期。'
    )

    config_list: list[dict] = [
        {
            "key": "qwin",
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
    ]


from clovers.core.config import config as clovers_config

config_key = __package__
config_data = Config.model_validate(clovers_config.get(config_key, {}))
"""主配置类"""
clovers_config[config_key] = config_data.model_dump()
