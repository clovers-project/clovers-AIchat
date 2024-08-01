from .config import config_data
from .main import plugin
from .qwin import build_Chat as build_QwinChat
from .hunyuan import build_Chat as build_HunYuanChat


config_list = config_data.config_list

for config_dict in config_list:
    key: str = config_dict["key"]
    match key:
        case "qwin":
            build_QwinChat(config_dict).new()
        case "hunyuan":
            build_HunYuanChat(config_dict).new()
        case _:
            raise ValueError(f"Invalid config key {key}")


__plugin__ = plugin
