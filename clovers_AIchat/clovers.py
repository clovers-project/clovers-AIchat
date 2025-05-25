from clovers import EventProtocol
from typing import Protocol


class Event(EventProtocol, Protocol):
    Bot_Nickname: str
    user_id: str
    group_id: str | None
    to_me: bool
    nickname: str
    image_list: list[str]
    permission: int
