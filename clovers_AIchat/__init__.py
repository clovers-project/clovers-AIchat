from .config import config_data
from .qwin import create_Chat as create_QwinChat
from .hunyuan import create_Chat as create_HunYuanChat
from .main import plugin, new_chat


config_list = config_data.config_list

for config_dict in config_list:
    match config_dict["key"]:
        case "qwin":
            new_chat(create_QwinChat(config_dict))
        case "hunyuan":
            new_chat(create_HunYuanChat(config_dict))
        case _:
            raise ValueError(f'Invalid config key {config_dict["key"]}')


__plugin__ = plugin
