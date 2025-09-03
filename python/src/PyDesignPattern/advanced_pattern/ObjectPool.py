#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 5/27/2018

# Version 1.0
#=======================================================================================================================
# class PowerBank:
#     """移動電源"""
#
#     def __init__(self, serialNum, electricQuantity):
#         self.__serialNum = serialNum
#         self.__electricQuantity = electricQuantity
#         self.__user = ""
#
#     def getSerialNum(self):
#         return self.__serialNum
#
#     def getElectricQuantity(self):
#         return self.__electricQuantity
#
#     def setUser(self, user):
#         self.__user = user
#
#     def getUser(self):
#         return self.__user
#
#     def showInfo(self):
#         print("序列號:%s 電量:%d%%  使用者:%s" % (self.__serialNum, self.__electricQuantity, self.__user) )


class ObjectPack:
    """對象的包裝類
    封裝指定的對象(如充電寶)是否被使用中"""
    def __init__(self, obj, inUsing = False):
        self.__obj = obj
        self.__inUsing = inUsing

    def inUsing(self):
        return self.__inUsing

    def setUsing(self, isUsing):
        self.__inUsing = isUsing

    def getObj(self):
        return self.__obj


class PowerBankBox:
    """存放移動電源的智能箱盒"""

    def __init__(self):
        self.__pools = {}
        self.__pools["0001"] = ObjectPack(PowerBank("0001", 100))
        self.__pools["0002"] = ObjectPack(PowerBank("0002", 100))

    def borrow(self, serialNum):
        """借用移動電源"""
        item = self.__pools.get(serialNum)
        result = None
        if(item is None):
            print("沒有可用的電源！")
        elif(not item.inUsing()):
            item.setUsing(True)
            result = item.getObj()
        else:
            print("%s電源 已被借用！" % serialNum)
        return result

    def giveBack(self, serialNum):
        """歸還移動電源"""
        item = self.__pools.get(serialNum)
        if(item is not None):
            item.setUsing(False)
            print("%s電源 已歸還!" % serialNum)


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
import logging
# 引入logging模塊用於輸出日誌信息
import time
# 引入時間模塊
logging.basicConfig(level=logging.INFO)
# 如果想在控制檯打印INFO以上的信息，則加上此配製

class PooledObject:
    """池對象,也稱池化對象"""

    def __init__(self, obj):
        self.__obj = obj
        self.__busy = False

    def getObject(self):
        return self.__obj

    def setObject(self, obj):
        self.__obj = obj

    def isBusy(self):
        return self.__busy

    def setBusy(self, busy):
        self.__busy = busy


class ObjectPool(metaclass=ABCMeta):
    """對象池"""

    """對象池初始化大小"""
    InitialNumOfObjects = 10
    """對象池最大的大小"""
    MaxNumOfObjects = 50

    def __init__(self):
        self.__pools = []
        for i in range(0, ObjectPool.InitialNumOfObjects):
            obj = self.createPooledObject()
            self.__pools.append(obj)

    @abstractmethod
    def createPooledObject(self):
        """創建池對象, 由子類實現該方法"""
        pass

    def borrowObject(self):
        """借用對象"""
        # 如果找到空閒對象，直接返回
        obj = self._findFreeObject()
        if(obj is not None):
            logging.info("%x對象已被借用, time:%s", id(obj),
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())) )
            return obj
        # 如果對象池未滿，則添加新的對象
        if(len(self.__pools) < ObjectPool.MaxNumOfObjects):
            pooledObj = self.addObject()
            if (pooledObj is not None):
                pooledObj.setBusy(True)
                logging.info("%x對象已被借用, time:%s", id(obj),
                             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                return pooledObj.getObject()
        # 對象池已滿且沒有空閒對象，則返回None
        return None

    def returnObject(self, obj):
        """歸還對象"""
        for pooledObj in self.__pools:
            if(pooledObj.getObject() == obj):
                pooledObj.setBusy(False)
                logging.info("%x對象已歸還, time:%s", id(obj),
                             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                break

    def addObject(self):
        """添加新對象"""
        obj = None
        if(len(self.__pools) < ObjectPool.MaxNumOfObjects):
            obj = self.createPooledObject()
            self.__pools.append(obj)
            logging.info("添加新對象%x, time:", id(obj),
                         time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        return obj

    def clear(self):
        """清空對象池"""
        self.__pools.clear()

    def _findFreeObject(self):
        """查找空閒的對象"""
        obj = None
        for pooledObj in self.__pools:
            if(not pooledObj.isBusy()):
                obj = pooledObj.getObject()
                pooledObj.setBusy(True)
                break
        return obj


# 基於框架的實現
#==============================
class PowerBank:
    """移動電源"""

    def __init__(self, serialNum, electricQuantity):
        self.__serialNum = serialNum
        self.__electricQuantity = electricQuantity
        self.__user = ""

    def getSerialNum(self):
        return self.__serialNum

    def getElectricQuantity(self):
        return self.__electricQuantity

    def setUser(self, user):
        self.__user = user

    def getUser(self):
        return self.__user

    def showInfo(self):
        print("序列號:%03d  電量:%d%%  使用者:%s" % (self.__serialNum, self.__electricQuantity, self.__user))

class PowerBankPool(ObjectPool):
    """存放移動電源的智能箱盒"""

    __serialNum = 0

    @classmethod
    def getSerialNum(cls):
        cls.__serialNum += 1
        return cls.__serialNum


    def createPooledObject(self):
        powerBank = PowerBank(PowerBankPool.getSerialNum(), 100)
        return PooledObject(powerBank)

# Test
#=======================================================================================================================
def testPowerBank():
    box = PowerBankBox()
    powerBank1 = box.borrow("0001")
    if(powerBank1 is not None):
        powerBank1.setUser("Tony")
        powerBank1.showInfo()
    powerBank2 = box.borrow("0002")
    if(powerBank2 is not None):
        powerBank2.setUser("Sam")
        powerBank2.showInfo()
    powerBank3 = box.borrow("0001")
    box.giveBack("0001")
    powerBank3 = box.borrow("0001")
    if(powerBank3 is not None):
        powerBank3.setUser("Aimee")
        powerBank3.showInfo()


def testObjectPool():
    powerBankPool = PowerBankPool()
    powerBank1 = powerBankPool.borrowObject()
    if (powerBank1 is not None):
        powerBank1.setUser("Tony")
        powerBank1.showInfo()
    powerBank2 = powerBankPool.borrowObject()
    if (powerBank2 is not None):
        powerBank2.setUser("Sam")
        powerBank2.showInfo()
    powerBankPool.returnObject(powerBank1)
    # powerBank1歸還後，不能再對其進行相關操作
    powerBank3 = powerBankPool.borrowObject()
    if (powerBank3 is not None):
        powerBank3.setUser("Aimee")
        powerBank3.showInfo()

    powerBankPool.returnObject(powerBank2)
    powerBankPool.returnObject(powerBank3)
    powerBankPool.clear()

# testPowerBank()
testObjectPool()

