#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 4/21/2018

# Version 1.0
#=======================================================================================================================
from enum import Enum
# Python3.4 之後支持枚舉Enum的語法

class ShapeType(Enum):
    "形狀類型"
    ShapeTypeLine = 1
    ShapeTypeRect = 2
    ShapeTypeEllipse = 3


class Shape:
    "形狀"

    def __init__(self, name):
        self.__name = name

    def getType(self):
        pass

    def getName(self):
        return self.__name


class Line(Shape):
    "直線"

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return ShapeType.ShapeTypeLine

class Rectangle(Shape):
    "矩形"

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return ShapeType.ShapeTypeRect


class Ellipse(Shape):
    "橢圓"

    def __init__(self, name):
        super().__init__(name)

    def getType(self):
        return ShapeType.ShapeTypeEllipse

class ShapeFactory:
    "形狀的工廠類"

    @staticmethod
    def createShape(self, type):
        pass

    def createPen(self, penType):
        "創建形狀"
        # Python中沒有switch/case的語法，我們通過字典來來模擬switch/case的實現方式
        switcher = {
            ShapeType.ShapeTypeLine : Line("直線"),
            ShapeType.ShapeTypeRect : Rectangle("矩形"),
            ShapeType.ShapeTypeEllipse : Ellipse("橢圓"),
        }
        return switcher.get(penType, "create pen error")

class ShapeType(Enum):
    "形狀類型"
    ColorRed = 1
    ColorGreen = 2
    ColorBlue = 3

class Color:
    "顏色"

    def __init__(self, value):
        self.__value = value

    def getType(self):
        pass

# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================


# 基於框架的實現
#==============================


# Test
#=======================================================================================================================

