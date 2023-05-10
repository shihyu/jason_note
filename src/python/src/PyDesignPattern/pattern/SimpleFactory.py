#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 12/2/2017

# Version 1.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Coffee(metaclass=ABCMeta):
    """咖啡"""

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    @abstractmethod
    def getTaste(self):
        pass


class LatteCaffe(Coffee):
    """拿鐵咖啡"""

    def __init__(self, name):
        super().__init__(name)

    def getTaste(self):
        return "輕柔而香醇"

class MochaCoffee(Coffee):
    """摩卡咖啡"""

    def __init__(self, name):
        super().__init__(name)

    def getTaste(self):
        return "絲滑與醇厚"

class Coffeemaker:
    """咖啡機"""

    @staticmethod
    def makeCoffee(coffeeBean):
        "通過staticmethod裝飾器修飾來定義一個靜態方法"
        if(coffeeBean == "拿鐵咖啡豆"):
            coffee = LatteCaffe("拿鐵咖啡")
        elif(coffeeBean == "摩卡咖啡豆"):
            coffee = MochaCoffee("摩卡咖啡")
        else:
            raise ValueError("不支持的參數：%s" % coffeeBean)
        return coffee



# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
from enum import Enum
# Python3.4 之後支持枚舉Enum的語法

class PenType(Enum):
    """畫筆類型"""
    PenTypeLine = 1
    PenTypeRect = 2
    PenTypeEllipse = 3


class Pen(metaclass=ABCMeta):
    """畫筆"""

    def __init__(self, name):
        self.__name = name

    @abstractmethod
    def getType(self):
        pass

    def getName(self):
        return self.__name


class LinePen(Pen):
    """直線畫筆"""

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return PenType.PenTypeLine

class RectanglePen(Pen):
    """矩形畫筆"""

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return PenType.PenTypeRect


class EllipsePen(Pen):
    """橢圓畫筆"""

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return PenType.PenTypeEllipse


class PenFactory:
    """畫筆工廠類"""

    def __init__(self):
        "定義一個字典(key:PenType，value：Pen)來存放對象,確保每一個類型只會有一個對象"
        self.__pens = {}

    def getSingleObj(self, penType, name):
        """獲得唯一實例的對象"""


    def createPen(self, penType):
        """創建畫筆"""
        if (self.__pens.get(penType) is None):
            # 如果該對象不存在，則創建一個對象並存到字典中
            if penType == PenType.PenTypeLine:
                pen = LinePen("直線畫筆")
            elif penType == PenType.PenTypeRect:
                pen = RectanglePen("矩形畫筆")
            elif penType == PenType.PenTypeEllipse:
                pen = EllipsePen("橢圓畫筆")
            else:
                pen = Pen("")
            self.__pens[penType] = pen
        # 否則直接返回字典中的對象
        return self.__pens[penType]


# 基於框架的實現
#==============================


# Test
#=======================================================================================================================
def testCoffeeMaker():
    latte = Coffeemaker.makeCoffee("拿鐵咖啡豆")
    print("%s已為您準備好了，口感：%s。請慢慢享用！" % (latte.getName(), latte.getTaste()) )
    mocha = Coffeemaker.makeCoffee("摩卡咖啡豆")
    print("%s已為您準備好了，口感：%s。請慢慢享用！" % (mocha.getName(), mocha.getTaste()))


def testPenFactory():
    factory = PenFactory()
    linePen = factory.createPen(PenType.PenTypeLine)
    print("創建了 %s，對象id：%s， 類型：%s" % (linePen.getName(), id(linePen), linePen.getType()) )
    rectPen = factory.createPen(PenType.PenTypeRect)
    print("創建了 %s，對象id：%s， 類型：%s" % (rectPen.getName(), id(rectPen), rectPen.getType()) )
    rectPen2 = factory.createPen(PenType.PenTypeRect)
    print("創建了 %s，對象id：%s， 類型：%s" % (rectPen2.getName(), id(rectPen2), rectPen2.getType()) )
    ellipsePen = factory.createPen(PenType.PenTypeEllipse)
    print("創建了 %s，對象id：%s， 類型：%s" % (ellipsePen.getName(), id(ellipsePen), ellipsePen.getType()) )


# testCoffeeMaker()
testPenFactory()