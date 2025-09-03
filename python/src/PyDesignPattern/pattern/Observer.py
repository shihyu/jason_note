##!/usr/bin/python

# Version 1.0
########################################################################################################################
# from abc import ABCMeta, abstractmethod
# # 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
#
# class WaterHeater:
#     """熱水器：戰勝寒冬的有利武器"""
#
#     def __init__(self):
#         self.__observers = []
#         self.__temperature = 25
#
#     def getTemperature(self):
#         return self.__temperature
#
#     def setTemperature(self, temperature):
#         self.__temperature = temperature
#         print("當前溫度是：" + str(self.__temperature) + "℃")
#         self.notifies()
#
#     def addObserver(self, observer):
#         self.__observers.append(observer)
#
#     def notifies(self):
#         for o in self.__observers:
#             o.update(self)
#
#
# class Observer(metaclass=ABCMeta):
#     "洗澡模式和飲用模式的父類"
#
#     @abstractmethod
#     def update(self, waterHeater):
#         pass
#
#
# class WashingMode(Observer):
#     """該模式用於洗澡"""
#
#     def update(self, waterHeater):
#         if waterHeater.getTemperature() >= 50 and waterHeater.getTemperature() < 70:
#             print("水已燒好！溫度正好，可以用來洗澡了。")
#
#
# class DrinkingMode(Observer):
#     """該模式用於飲用"""
#
#     def update(self, waterHeater):
#         if waterHeater.getTemperature() >= 100:
#             print("水已燒開！可以用來飲用了。")


# Version 2.0
########################################################################################################################
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Observer(metaclass=ABCMeta):
    """觀察者的基類"""

    @abstractmethod
    def update(self, observable, object):
        pass


class Observable:
    """被觀察者的基類"""

    def __init__(self):
        self.__observers = []

    def addObserver(self, observer):
        self.__observers.append(observer)

    def removeObserver(self, observer):
        self.__observers.remove(observer)

    def notifyObservers(self, object=0):
        for o in self.__observers:
            o.update(self, object)


class WaterHeater(Observable):
    """熱水器：戰勝寒冬的有利武器"""

    def __init__(self):
        super().__init__()
        self.__temperature = 25

    def getTemperature(self):
        return self.__temperature

    def setTemperature(self, temperature):
        self.__temperature = temperature
        print("當前溫度是：" + str(self.__temperature) + "℃")
        self.notifyObservers()


class WashingMode(Observer):
    """該模式用於洗澡用"""

    def update(self, observable, object):
        if isinstance(observable, WaterHeater) \
                and observable.getTemperature() >= 50 and observable.getTemperature() < 70:
            print("水已燒好！溫度正好，可以用來洗澡了。")


class DrinkingMode(Observer):
    "該模式用於飲用"

    def update(self, observable, object):
        if isinstance(observable, WaterHeater) and observable.getTemperature() >= 100:
            print("水已燒開！可以用來飲用了。")


import time
# 導入時間處理模塊

class Account(Observable):
    """用戶賬戶"""

    def __init__(self):
        super().__init__()
        self.__latestIp = {}
        self.__latestRegion = {}

    def login(self, name, ip, time):
        region = self.__getRegion(ip)
        if self.__isLongDistance(name, region):
            self.notifyObservers({"name": name, "ip": ip, "region": region, "time": time})
        self.__latestRegion[name] = region
        self.__latestIp[name] = ip

    def __getRegion(self, ip):
        # 由IP地址獲取地區信息。這裡只是模擬，真實項目中應該調用IP地址解析服務
        ipRegions = {
            "101.47.18.9": "浙江省杭州市",
            "67.218.147.69":"美國洛杉磯"
        }
        region = ipRegions.get(ip)
        return "" if region is None else region


    def __isLongDistance(self, name, region):
        # 計算本次登錄與最近幾次登錄的地區差距。
        # 這裡只是簡單地用字符串匹配來模擬，真實的項目中應該調用地理信息相關的服務
        latestRegion = self.__latestRegion.get(name)
        return latestRegion is not None and latestRegion != region;


class SmsSender(Observer):
    """短信發送器"""

    def update(self, observable, object):
        print("[短信發送] " + object["name"] + "您好！檢測到您的賬戶可能登錄異常。最近一次登錄信息：\n"
              + "登錄地區：" + object["region"] + "  登錄ip：" + object["ip"] + "  登錄時間："
              + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(object["time"])))


class MailSender(Observer):
    """郵件發送器"""

    def update(self, observable, object):
        print("[郵件發送] " + object["name"] + "您好！檢測到您的賬戶可能登錄異常。最近一次登錄信息：\n"
              + "登錄地區：" + object["region"] + "  登錄ip：" + object["ip"] + "  登錄時間："
              + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(object["time"])))


def testWaterHeater():
    heater = WaterHeater()
    washingObser = WashingMode()
    drinkingObser = DrinkingMode()
    heater.addObserver(washingObser)
    heater.addObserver(drinkingObser)
    heater.setTemperature(40)
    heater.setTemperature(60)
    heater.setTemperature(100)


def testLogin():
    accout = Account()
    accout.addObserver(SmsSender())
    accout.addObserver(MailSender())
    accout.login("Tony", "101.47.18.9", time.time())
    accout.login("Tony", "67.218.147.69", time.time())



def testTime():
    print(time.time())
    strTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    print(strTime)

# testWaterHeater()
testLogin()
# testTime()

# ipRegion = {
#             "101.47.18.9": "浙江省杭州市",
#             "67.218.147.69":"美國洛杉磯"
#         }
#
# print(ipRegion["101.47.18.90"])
