#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 4/6/2018

# Version 1.0
#=======================================================================================================================
# from abc import ABCMeta, abstractmethod
# # 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
#
# class Toy(metaclass=ABCMeta):
#     """玩具"""
#
#     def __init__(self, name):
#         self._name = name
#         self.__components = []
#
#     def getName(self):
#         return self._name
#
#     def addComponent(self, component, count = 1, unit = "個"):
#         self.__components.append([component, count, unit])
#         print("%s 增加了 %d %s%s" % (self._name, count, unit, component) );
#
#     @abstractmethod
#     def feature(self):
#         pass
#
#
# class Car(Toy):
#     """小車"""
#
#     def feature(self):
#         print("我是 %s，我可以快速奔跑……" % self._name)
#
#
# class Manor(Toy):
#     """莊園"""
#
#     def feature(self):
#         print("我是 %s，我可供觀賞，也可用來遊玩！" % self._name)
#
#
# class ToyBuilder:
#     """玩具構建者"""
#
#     def buildCar(self):
#         car = Car("迷你小車")
#         print("正在構建 %s ……" % car.getName())
#         car.addComponent("輪子", 4)
#         car.addComponent("車身", 1)
#         car.addComponent("發動機", 1)
#         car.addComponent("方向盤")
#         return car
#
#     def buildManor(self):
#         manor = Manor("淘淘小莊園")
#         print("正在構建 %s ……" % manor.getName())
#         manor.addComponent('客廳', 1, "間")
#         manor.addComponent('臥室', 2, "間")
#         manor.addComponent("書房", 1, "間")
#         manor.addComponent("廚房", 1, "間")
#         manor.addComponent("花園", 1, "個")
#         manor.addComponent("圍牆", 1, "堵")
#         return manor
#
#
# # Test
# #==============================
# def testBuilder():
#     builder = ToyBuilder()
#     car = builder.buildCar()
#     car.feature()
#
#     print()
#     mannor = builder.buildManor()
#     mannor.feature()




# Version 2.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Toy(metaclass=ABCMeta):
    """玩具"""

    def __init__(self, name):
        self._name = name
        self.__components = []

    def getName(self):
        return self._name

    def addComponent(self, component, count = 1, unit = "個"):
        self.__components.append([component, count, unit])
        # print("%s 增加了 %d %s%s" % (self._name, count, unit, component) );

    @abstractmethod
    def feature(self):
        pass


class Car(Toy):
    """小車"""

    def feature(self):
        print("我是 %s，我可以快速奔跑……" % self._name)


class Manor(Toy):
    """莊園"""

    def feature(self):
        print("我是 %s，我可供觀賞，也可用來遊玩！" % self._name)


class ToyBuilder(metaclass=ABCMeta):
    """玩具構建者"""

    @abstractmethod
    def buildProduct(self):
        pass


class CarBuilder(ToyBuilder):
    """車的構建類"""

    def buildProduct(self):
        car = Car("迷你小車")
        print("正在構建 %s ……" % car.getName())
        car.addComponent("輪子", 4)
        car.addComponent("車身", 1)
        car.addComponent("發動機", 1)
        car.addComponent("方向盤")
        return car


class ManorBuilder(ToyBuilder):
    """莊園的構建類"""

    def buildProduct(self):
        manor = Manor("淘淘小莊園")
        print("正在構建 %s ……" % manor.getName())
        manor.addComponent('客廳', 1, "間")
        manor.addComponent('臥室', 2, "間")
        manor.addComponent("書房", 1, "間")
        manor.addComponent("廚房", 1, "間")
        manor.addComponent("花園", 1, "個")
        manor.addComponent("圍牆", 1, "堵")
        return manor

class BuilderMgr:
    """建構類的管理類"""

    def __init__(self):
        self.__carBuilder = CarBuilder()
        self.__manorBuilder = ManorBuilder()

    def buildCar(self, num):
        count = 0
        products = []
        while(count < num):
            car = self.__carBuilder.buildProduct()
            products.append(car)
            count +=1
            print("建造完成第 %d 輛 %s" % (count, car.getName()) )
        return products

    def buildManor(self, num):
        count = 0
        products = []
        while (count < num):
            manor = self.__manorBuilder.buildProduct()
            products.append(manor)
            count += 1
            print("建造完成第 %d 個 %s" % (count, manor.getName()))
        return products


# Test
# ==============================
def testAdvancedBuilder():
    builderMgr = BuilderMgr()
    builderMgr.buildManor(2)
    print()
    builderMgr.buildCar(4)


# testBuilder()
testAdvancedBuilder()
