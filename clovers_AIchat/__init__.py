from .config import config_data
from .qwin import Chat as QwinChat
from .hunyuan import Chat as HunYuanChat
from .main import create_chat, plugin


create_chat(config_data.qwin_whitegroups, config_data.qwin_blackgroups, QwinChat)
create_chat(config_data.hunyuan_whitegroups, config_data.hunyuan_blackgroups, HunYuanChat)


__plugin__ = plugin
