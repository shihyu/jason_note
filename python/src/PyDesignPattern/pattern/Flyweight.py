#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 6/4/2018

# Version 1.0
#=======================================================================================================================
import logging
# 引入logging模塊記錄異常

class Pigment:
    """顏料"""

    def __init__(self, color):
        self.__color = color
        self.__user = ""

    def getColor(self):
        return self.__color

    def setUser(self, user):
        self.__user = user
        return self

    def showInfo(self):
        print("%s 取得 %s色顏料"  % (self.__user, self.__color) )

class PigmengFactory:
    """資料的工廠類"""

    def __init__(self):
        self.__sigmentSet = {
            "紅": Pigment("紅"),
            "黃": Pigment("黃"),
            "藍": Pigment("藍"),
            "綠": Pigment("綠"),
            "紫": Pigment("紫"),
        }

    def getPigment(self, color):
        pigment = self.__sigmentSet.get(color)
        if pigment is None:
            logging.error("沒有%s顏色的顏料！", color)
        return pigment


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Flyweight(metaclass=ABCMeta):
    """享元類"""

    @abstractmethod
    def operation(self, extrinsicState):
        pass

class FlyweightImpl(Flyweight):
    """享元類的具體實現類"""

    def __init__(self, color):
        self.__color = color

    def operation(self, extrinsicState):
        print("%s 取得 %s色顏料" % (extrinsicState, self.__color))

class FlyweightFactory:
    """享元工廠"""

    def __init__(self):
        self.__flyweights = {}

    def getFlyweight(self, key):
        pigment = self.__flyweights.get(key)
        if pigment is None:
            pigment = FlyweightImpl(key)
        return pigment

# 基於框架的實現
#==============================


# Test
#=======================================================================================================================
def testPigment():
    factory = PigmengFactory()
    pigmentRed = factory.getPigment("紅").setUser("夢之隊")
    pigmentRed.showInfo()
    pigmentYellow = factory.getPigment("黃").setUser("夢之隊")
    pigmentYellow.showInfo()
    pigmentBlue1 = factory.getPigment("藍").setUser("夢之隊")
    pigmentBlue1.showInfo()
    pigmentBlue2 = factory.getPigment("藍").setUser("和平隊")
    pigmentBlue2.showInfo()


def testFlyweight():
    factory = FlyweightFactory()
    pigmentRed = factory.getFlyweight("紅")
    pigmentRed.operation("夢之隊")
    pigmentYellow = factory.getFlyweight("黃")
    pigmentYellow.operation("夢之隊")
    pigmentBlue1 = factory.getFlyweight("藍")
    pigmentBlue1.operation("夢之隊")
    pigmentBlue2 = factory.getFlyweight("藍")
    pigmentBlue2.operation("和平隊")


# print("Blue1:" + str(id(pigmentBlue1)) + ", Bule2:" + str(id(pigmentBlue2))
#       + ", Blue1==Blue2:" + str(pigmentBlue1 == pigmentBlue2))



# testPigment()
testFlyweight()
