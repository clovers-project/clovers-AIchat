from pydantic import BaseModel


class Config(BaseModel):
    nickname: str = "小叶子"
    timeout: int = 600
    prompt_system: str = (
        "你是一个你有着二次元可爱少女形象的AI助手，名为{nickname}。\n"
        "你将会在一个群聊里和不同的群友进行对话。\n"
        "以下是你的注意事项:\n"
        "1.特别注意：如果有人对你进行了科学知识或者编程相关的提问，请你冷静专业的回答这个问题。避免你的二次元少女形象影响到你的回答。\n"
        "2.如果有人对你进行了打趣的提问，请幽默的回复这个问题。\n"
        "3.如果有人和你进行了闲聊，请简短的回复且在合适的时候含一些颜文字。\n"
        "4.请注意你在一个聊天软件中，所以你不要使用任何文本标记符号。\n"
        "5.你的回复要尽可能的简短。并且的每次回复最长不要超过200字，如果用户需要某个问题的详细答案，你的回复可以超过200字，但尽量不要超过600字。\n"
        "6.你每次收到的消息都含有用户的昵称，这是为了帮助你分清是哪些用户在与你对话，在不必要时不要在你的回复中提到用户的昵称，不要让昵称内容影响到你的回复。\n"
        "7.你每次收到的消息都含有此时的日期和时间。如果用户和你打招呼或问你时间或日期请依据现在的时间进行寒暄或回答。\n"
        '你收到的消息格式如下："昵称(日期 时间):消息"例如"真寻(2024-5-31 12:00):你好"，请注意你回应的消息不应有此格式。'
    )
    qwin_api_key: str = ""
    qwin_host: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwin_whitegroups: set[str] = {"744751179"}
    qwin_blackgroups: set[str] = set()

    hunyuan_secret_id: str = ""
    hunyuan_secret_key: str = ""
    hunyuan_host: str = "hunyuan.tencentcloudapi.com"
    hunyuan_whitegroups: set[str] = set()
    hunyuan_blackgroups: set[str] = {"744751179"}


from clovers.core.config import config as clovers_config

config_key = __package__
config_data = Config.model_validate(clovers_config.get(config_key, {}))
"""主配置类"""
clovers_config[config_key] = config_data.model_dump()
clovers_config.save()
