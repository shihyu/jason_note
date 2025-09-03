#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 9/24/2018

# Python中的裝飾器
#=======================================================================================================================
# Python中函數的特殊功能
#==============================
def func(num):
    """定義內部函數並返回"""

    def firstInnerFunc():
        return "這是第一個內部函數"

    def secondInnerFunc():
        return "這是第二個內部函數"

    if num == 1:
        return firstInnerFunc
    else:
        return secondInnerFunc


# print(func(1))
# print(func(2))
# print(func(1)())
# print(func(2)())


# firstFunc = func(1)
# secondFunc = func(2)
# print(firstFunc)
# print(secondFunc)
# print(firstFunc())
# print(secondFunc())


# 裝飾器修飾函數
#==============================
import logging
logging.basicConfig(level=logging.INFO)

def loggingDecorator(func):
    """記錄日誌的裝飾器"""
    def wrapperLogging(*args, **kwargs):
        logging.info("開始執行 %s() ..." % func.__name__)
        func(*args, **kwargs)
        logging.info("%s() 執行完成！" % func.__name__)
    return wrapperLogging

def showInfo(*args, **kwargs):
    print("這是一個測試函數，參數：", args, kwargs)


# decoratedShowInfo = loggingDecorator(showInfo)
# decoratedShowInfo('arg1', 'arg2', kwarg1 = 1, kwarg2 = 2)


# def showMin(a, b):
#     print("%d、%d 中的最小值是：%d" % (a, b, a + b))
#
# decoratedShowMin = loggingDecorator(showMin)
# decoratedShowMin(2, 3)


# @loggingDecorator
# def showMin(a, b):
#     print("%d、%d 中的最小值是：%d" % (a, b, a + b))
#
# showMin(2, 3)


# 裝飾器修飾類
#==============================
class ClassDecorator:
    """類裝飾器，記錄一個類被實例化的次數"""

    def __init__(self, func):
        self.__numOfCall = 0
        self.__func = func

    def __call__(self, *args, **kwargs):
        self.__numOfCall += 1
        obj = self.__func(*args, *kwargs)
        print("創建%s的第%d個實例:%s" % (self.__func.__name__, self.__numOfCall, id(obj)))
        return obj

@ClassDecorator
class MyClass:

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name


tony = MyClass("Tony")
karry = MyClass("Karry")
print(id(tony))
print(id(karry))
