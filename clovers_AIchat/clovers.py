from clovers.core.plugin import Event as CloversEvent


class Event:
    def __init__(self, event: CloversEvent):
        self.event: CloversEvent = event

    @property
    def nickname(self) -> str:
        return self.event.kwargs["nickname"]

    @property
    def group_id(self) -> str:
        return self.event.kwargs["group_id"]

    @property
    def to_me(self) -> bool:
        return self.event.kwargs["to_me"]

    @property
    def permission(self) -> int:
        return self.event.kwargs["permission"]
