#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 4/24/2018

# Version 1.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Chef():
    """廚師"""

    def steamFood(self, originalMaterial):
        print("%s清蒸中..." % originalMaterial)
        return "清蒸" + originalMaterial

    def stirFriedFood(self, originalMaterial):
        print("%s爆炒中..." % originalMaterial)
        return "香辣炒" + originalMaterial

class Order(metaclass=ABCMeta):
    """訂單"""

    def __init__(self, name, originalMaterial):
        self._chef = Chef()
        self._name = name
        self._originalMaterial = originalMaterial

    def getDisplayName(self):
        return self._name + self._originalMaterial

    @abstractmethod
    def processingOrder(self):
        pass

class SteamedOrder(Order):
    """清蒸"""

    def __init__(self, originalMaterial):
        super().__init__("清蒸", originalMaterial)

    def processingOrder(self):
        if(self._chef is not None):
            return self._chef.steamFood(self._originalMaterial)
        return ""


class SpicyOrder(Order):
    """香辣炒"""

    def __init__(self, originalMaterial):
        super().__init__("香辣炒", originalMaterial)

    def processingOrder(self):
        if (self._chef is not None):
            return self._chef.stirFriedFood(self._originalMaterial)
        return ""


class Waiter:
    """服務員"""

    def __init__(self, name):
        self.__name = name
        self.__order = None

    def receiveOrder(self, order):
        self.__order = order
        print("服務員%s：您的 %s 訂單已經收到,請耐心等待" % (self.__name, order.getDisplayName()) )

    def placeOrder(self):
        food = self.__order.processingOrder()
        print("服務員%s：您的餐 %s 已經準備好，請您慢用!" % (self.__name, food) )



# class Customer:
#     "顧客"
#
#     def __init__(self, name):
#         self.__name = name
#
#     def order(self):

# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Command(metaclass=ABCMeta):
    """命令的抽象類"""

    @abstractmethod
    def execute(self):
        pass

class CommandImpl(Command):
    """命令的具體實現類"""

    def __init__(self, receiver):
        self.__receiver = receiver

    def execute(self):
        self.__receiver.doSomething()

class Receiver:
    """命令的接收者"""

    def doSomething(self):
        print("do something...")

class Invoker:
    """調度者"""

    def __init__(self):
        self.__command = None

    def setCommand(self, command):
        self.__command = command

    def action(self):
        if self.__command is not None:
            self.__command.execute()


# 基於框架的實現
#==============================

# Test
#=======================================================================================================================

def testOrder():
    waiter = Waiter("Anna")
    steamedOrder = SteamedOrder("大閘蟹")
    print("客戶David：我要一份 %s" % steamedOrder.getDisplayName())
    waiter.receiveOrder(steamedOrder)
    waiter.placeOrder()
    print()

    spicyOrder = SpicyOrder("大閘蟹")
    print("客戶Tony：我要一份 %s" % spicyOrder.getDisplayName())
    waiter.receiveOrder(spicyOrder)
    waiter.placeOrder()


def client():
    invoker = Invoker()
    command = CommandImpl(Receiver())
    invoker.setCommand(command)
    invoker.action()


# testOrder()
client()

