#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 8/7/2018

# Open Close Principle，OCP



# class Zoo:
#     """動物園"""
#
#     def __init__(self):
#         self.__animals =[
#             TerrestrialAnimal("狗"),
#             AquaticAnimal("魚")
#         ]
#
#     def displayActivity(self):
#         for animal in self.__animals:
#             if isinstance(animal, TerrestrialAnimal):
#                 animal.running()
#             else:
#                 animal.swimming()
#
# zoo = Zoo()
# zoo.displayActivity()



# def displayActivity(self):
# 	for animal in self.__animals:
# 		if isinstance(animal, TerrestrialAnimal):
# 			animal.running()
# 		elif isinstance(animal, BirdAnimal)
# 			animal.flying()
# 		else:
# 			animal.swimming()



from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Animal(metaclass=ABCMeta):
    """動物"""

    def __init__(self, name):
        self._name = name

    @abstractmethod
    def moving(self):
        pass

class TerrestrialAnimal(Animal):
    """陸生生物"""

    def __init__(self, name):
        super().__init__(name)

    def moving(self):
        print(self._name + "在陸上跑...")


class AquaticAnimal(Animal):
    """水生生物"""

    def __init__(self, name):
        super().__init__(name)

    def moving(self):
        print(self._name + "在水裡遊...")


class BirdAnimal(Animal):
    """鳥類動物"""

    def __init__(self, name):
        super().__init__(name)

    def moving(self):
        print(self._name + "在天空飛...")


class Zoo:
    """動物園"""

    def __init__(self):
        self.__animals =[]

    def addAnimal(self, animal):
        self.__animals.append(animal)

    def displayActivity(self):
        print("觀察每一種動物的活動方式：")
        for animal in self.__animals:
            animal.moving()


def testZoo():
    zoo = Zoo()
    zoo.addAnimal(TerrestrialAnimal("狗"))
    zoo.addAnimal(AquaticAnimal("魚"))
    zoo.addAnimal(BirdAnimal("鳥"))
    zoo.displayActivity()



testZoo()