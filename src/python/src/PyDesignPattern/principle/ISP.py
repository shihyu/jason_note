#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 8/7/2018

# Interface Segregation Principle(ISP)


from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Animal(metaclass=ABCMeta):
    """(脊椎)動物"""

    def __init__(self, name):
        self._name = name

    def getName(self):
        return self._name

    @abstractmethod
    def feature(self):
        pass

    @abstractmethod
    def moving(self):
        pass


class IRunnable(metaclass=ABCMeta):
    """奔跑的接口"""

    @abstractmethod
    def running(self):
        pass

class IFlyable(metaclass=ABCMeta):
    """飛行的接口"""

    @abstractmethod
    def flying(self):
        pass

class INatatory(metaclass=ABCMeta):
    """游泳的接口"""

    @abstractmethod
    def swimming(self):
        pass


class MammalAnimal(Animal, IRunnable):
    """哺乳動物"""

    def __init__(self, name):
        super().__init__(name)

    def feature(self):
        print(self._name + "的生理特徵：恆溫，胎生，哺乳。")

    def running(self):
        print("在陸上跑...")

    def moving(self):
        print(self._name + "的活動方式：", end="")
        self.running()


class BirdAnimal(Animal, IFlyable):
    """鳥類動物"""

    def __init__(self, name):
        super().__init__(name)

    def feature(self):
        print(self._name + "的生理特徵：恆溫，卵生，前肢成翅。")

    def flying(self):
        print("在天空飛...")

    def moving(self):
        print(self._name + "的活動方式：", end="")
        self.flying()

class FishAnimal(Animal, INatatory):
    """魚類動物"""

    def __init__(self, name):
        super().__init__(name)

    def feature(self):
        print(self._name + "的生理特徵：流線型體形，用鰓呼吸。")

    def swimming(self):
        print("在水裡遊...")

    def moving(self):
        print(self._name + "的活動方式：", end="")
        self.swimming()


class Bat(MammalAnimal, IFlyable):
    """蝙蝠"""

    def __init__(self, name):
        super().__init__(name)

    def running(self):
        print("行走功能已經退化。")

    def flying(self):
        print("在天空飛...", end="")

    def moving(self):
        print(self._name + "的活動方式：", end="")
        self.flying()
        self.running()

class Swan(BirdAnimal, IRunnable, INatatory):
    """天鵝"""

    def __init__(self, name):
        super().__init__(name)

    def running(self):
        print("在陸上跑...", end="")

    def swimming(self):
        print("在水裡遊...", end="")

    def moving(self):
        print(self._name + "的活動方式：", end="")
        self.running()
        self.swimming()
        self.flying()

class CrucianCarp(FishAnimal):
    """鯽魚"""

    def __init__(self, name):
        super().__init__(name)


def testAnimal():
    bat = Bat("蝙蝠")
    bat.feature()
    bat.moving()
    swan = Swan("天鵝")
    swan.feature()
    swan.moving()
    crucianCarp = CrucianCarp("鯽魚")
    crucianCarp.feature()
    crucianCarp.moving()


testAnimal()