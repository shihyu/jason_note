#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 11/26/2017

# Version 1.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Person(metaclass=ABCMeta):
    """人"""

    def __init__(self, name):
        self._name = name

    @abstractmethod
    def wear(self):
        print("著裝：")


class Engineer(Person):
    """工程師"""

    def __init__(self, name, skill):
        super().__init__(name)
        self.__skill = skill

    def getSkill(self):
        return self.__skill

    def wear(self):
        print("我是 " + self.getSkill() + "工程師 " + self._name, end="， ")
        super().wear()

class Teacher(Person):
    "教師"

    def __init__(self, name, title):
        super().__init__(name)
        self.__title = title

    def getTitle(self):
        return self.__title

    def wear(self):
        print("我是 " + self._name + self.getTitle(), end="， ")
        super().wear()

class ClothingDecorator(Person):
    """服裝裝飾器的基類"""

    def __init__(self, person):
        self._decorated = person

    def wear(self):
        self._decorated.wear()
        self.decorate()

    @abstractmethod
    def decorate(self):
        pass


class CasualPantDecorator(ClothingDecorator):
    """休閒褲裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一條卡其色休閒褲")


class BeltDecorator(ClothingDecorator):
    """腰帶裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一條銀色針釦頭的黑色腰帶")

class LeatherShoesDecorator(ClothingDecorator):
    """皮鞋裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一雙深色休閒皮鞋")

class KnittedSweaterDecorator(ClothingDecorator):
    """針織毛衣裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一件紫紅色針織毛衣")


class WhiteShirtDecorator(ClothingDecorator):
    """白色襯衫裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一件白色襯衫")


class GlassesDecorator(ClothingDecorator):
    """眼鏡裝飾器"""

    def __init__(self, person):
        super().__init__(person)

    def decorate(self):
        print("一副方形黑框眼鏡")




# Test
#=======================================================================================================================
def testDecorator():
    tony = Engineer("Tony", "客戶端")
    pant = CasualPantDecorator(tony)
    belt = BeltDecorator(pant)
    shoes = LeatherShoesDecorator(belt)
    shirt = WhiteShirtDecorator(shoes)
    sweater = KnittedSweaterDecorator(shirt)
    glasses = GlassesDecorator(sweater)
    glasses.wear()

    print()
    decorateTeacher = GlassesDecorator(WhiteShirtDecorator(LeatherShoesDecorator(Teacher("wells", "教授"))))
    decorateTeacher.wear()


def testDecorator2():
    tony = Engineer("Tony", "客戶端")
    sweater = KnittedSweaterDecorator(tony)
    shirt = WhiteShirtDecorator(sweater)
    glasses = GlassesDecorator(shirt)
    glasses.wear()

# testDecorator()
# testDecorator2()