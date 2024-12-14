from abc import ABC, abstractmethod


class BaseAct(ABC):
    @abstractmethod
    def func(self): ...

    def run(self):
        print("run")
        self.func()
        print("end")

    def __init__(self) -> None:
        self.name = "BaseAct"
        self.call_count = 0


class Act1(BaseAct):
    def func(self):
        print(self.name)
        self.call_count += 1


class Act2(BaseAct):
    def func(self):
        print(self.name + " Act2")
        self.call_count += 1


act1 = Act1()
act2 = Act2()
print(act1.run())
print(act2.run())
print(act1.call_count)
print(act2.call_count)
