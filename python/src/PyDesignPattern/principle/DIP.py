#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 8/7/2018

# Dependence Inversion Principle, 簡稱DIP

from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Animal(metaclass=ABCMeta):
    """動物"""

    def __init__(self, name):
        self._name = name

    def eat(self, food):
        if(self.checkFood(food)):
            print(self._name + "進食" + food.getName())
        else:
            print(self._name + "不吃" + food.getName())

    @abstractmethod
    def checkFood(self, food):
        """檢查哪種食物能吃"""
        pass


class Dog(Animal):
    """狗"""

    def __init__(self):
        super().__init__("狗")

    def checkFood(self, food):
        return food.category() == "肉類"


class Swallow(Animal):
    """燕子"""

    def __init__(self):
        super().__init__("燕子")

    def checkFood(self, food):
        return food.category() == "昆蟲"


class Food(metaclass=ABCMeta):
    """食物"""

    def __init__(self, name):
        self._name = name

    def getName(self):
        return self._name

    @abstractmethod
    def category(self):
        """食物類別"""
        pass

    @abstractmethod
    def nutrient(self):
        """營養成分"""
        pass


class Meat(Food):
    """肉"""

    def __init__(self):
        super().__init__("肉")

    def category(self):
        return "肉類"

    def nutrient(self):
        return "蛋白質、脂肪"


class Worm(Food):
    """蟲子"""

    def __init__(self):
        super().__init__("蟲子")

    def category(self):
        return "昆蟲"

    def nutrient(self):
        return "蛋白質含、微量元素"


def testFood():
    dog = Dog()
    swallow = Swallow()
    meat = Meat()
    worm = Worm()
    dog.eat(meat)
    dog.eat(worm)
    swallow.eat(meat)
    swallow.eat(worm)


testFood()