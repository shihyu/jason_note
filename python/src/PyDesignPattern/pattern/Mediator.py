#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 11/17/2017

# Version 1.0
#=======================================================================================================================
class HouseInfo:
    """房源信息"""

    def __init__(self, area, price, hasWindow, hasBathroom, hasKitchen, address, owner):
        self.__area = area
        self.__price = price
        self.__hasWindow = hasWindow
        self.__hasBathroom = hasBathroom
        self.__hasKitchen = hasKitchen
        self.__address = address
        self.__owner = owner

    def getAddress(self):
        return self.__address

    def getOwnerName(self):
        return self.__owner.getName()

    def showInfo(self, isShowOwner = True):
        print("面積:" + str(self.__area) + "平米",
              "價格:" + str(self.__price) + "元",
              "窗戶:" + ("有" if self.__hasWindow else "沒有"),
              "衛生間:" + self.__hasBathroom,
              "廚房:" + ("有" if self.__hasKitchen else "沒有"),
              "地址:" + self.__address,
              "房東:" + self.getOwnerName() if isShowOwner else "")


class HousingAgency:
    """房屋中介"""

    def __init__(self, name):
        self.__houseInfos = []
        self.__name = name

    def getName(self):
        return self.__name

    def addHouseInfo(self, houseInfo):
        self.__houseInfos.append(houseInfo)

    def removeHouseInfo(self, houseInfo):
        for info in self.__houseInfos:
            if(info == houseInfo):
                self.__houseInfos.remove(info)

    def getSearchCondition(self, description):
        """這裡有一個將用戶描述信息轉換成搜索條件的邏輯
        (為節省篇幅這裡原樣返回描述)"""
        return description

    def getMatchInfos(self, searchCondition):
        """根據房源信息的各個屬性查找最匹配的信息
        (為節省篇幅這裡略去匹配的過程，全部輸出)"""
        print(self.getName(), "為您找到以下最適合的房源：")
        for info in self.__houseInfos:
            info.showInfo(False)
        return  self.__houseInfos

    def signContract(self, houseInfo, period):
        """與房東簽訂協議"""
        print(self.getName(), "與房東", houseInfo.getOwnerName(), "簽訂", houseInfo.getAddress(),
              "的房子的的租賃合同，租期", period, "年。 合同期內", self.getName(), "有權對其進行使用和轉租！")

    def signContracts(self, period):
        for info in self.__houseInfos :
            self.signContract(info, period)


class HouseOwner:
    """房東"""

    def __init__(self, name):
        self.__name = name
        self.__houseInfo = None

    def getName(self):
        return self.__name

    def setHouseInfo(self, address, area, price, hasWindow, bathroom, kitchen):
        self.__houseInfo = HouseInfo(area, price, hasWindow, bathroom, kitchen, address, self)

    def publishHouseInfo(self, agency):
        agency.addHouseInfo(self.__houseInfo)
        print(self.getName() + "在", agency.getName(), "發佈房源出租信息：")
        self.__houseInfo.showInfo()


class Customer:
    """用戶，租房的貧下中農"""

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def findHouse(self, description, agency):
        print("我是" + self.getName() + ", 我想要找一個\"" + description + "\"的房子")
        print()
        return agency.getMatchInfos(agency.getSearchCondition(description))

    def seeHouse(self, houseInfos):
        """去看房，選擇最使用的房子
        (這裡省略看房的過程)"""
        size = len(houseInfos)
        return houseInfos[size-1]

    def signContract(self, houseInfo, agency, period):
        """與中介簽訂協議"""
        print(self.getName(), "與中介", agency.getName(), "簽訂", houseInfo.getAddress(),
              "的房子的租賃合同, 租期", period, "年。合同期內", self.__name, "有權對其進行使用！")

# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
class InteractiveObject:
    """進行交互的對象"""
    pass

class InteractiveObjectImplA:
    """實現類A"""
    pass

class InteractiveObjectImplB:
    """實現類B"""
    pass

class Meditor:
    """中介類"""

    def __init__(self):
        self.__interactiveObjA = InteractiveObjectImplA()
        self.__interactiveObjB = InteractiveObjectImplB()

    def interative(self):
        """進行交互的操作"""
        # 通過self.__interactiveObjA和self.__interactiveObjB完成相應的交互操作
        pass


# 基於框架的實現
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
from enum import Enum
# Python3.4 之後支持枚舉Enum的語法

class DeviceType(Enum):
    "設備類型"
    TypeSpeaker = 1
    TypeMicrophone = 2
    TypeCamera = 3

class DeviceItem:
    """設備項"""

    def __init__(self, id, name, type, isDefault = False):
        self.__id = id
        self.__name = name
        self.__type = type
        self.__isDefault = isDefault

    def __str__(self):
        return "type:" + str(self.__type) + " id:" + str(self.__id) \
               + " name:" + str(self.__name) + " isDefault:" + str(self.__isDefault)

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getType(self):
        return self.__type

    def isDefault(self):
        return self.__isDefault


class DeviceList:
    """設備列表"""

    def __init__(self):
        self.__devices = []

    def add(self, deviceItem):
        self.__devices.append(deviceItem)

    def getCount(self):
        return len(self.__devices)

    def getByIdx(self, idx):
        if idx < 0 or idx >= self.getCount():
            return None
        return self.__devices[idx]

    def getById(self, id):
        for item in self.__devices:
            if( item.getId() == id):
                return item
        return None

class DeviceMgr(metaclass=ABCMeta):

    @abstractmethod
    def enumerate(self):
        """枚舉設備列表
        (在程序初始化時，有設備插拔時都要重新獲取設備列表)"""
        pass

    @abstractmethod
    def active(self, deviceId):
        """選擇要使用的設備"""
        pass

    @abstractmethod
    def getCurDeviceId(self):
        """獲取當前正在使用的設計ID"""
        pass


class SpeakerMgr(DeviceMgr):
    """揚聲器設備管理類"""

    def __init__(self):
        self.__curDeviceId = None

    def enumerate(self):
        """枚舉設備列表
        (真實的項目應該通過驅動程序去讀取設備信息，這裡只用初始化來模擬)"""
        devices = DeviceList()
        devices.add(DeviceItem("369dd760-893b-4fe0-89b1-671eca0f0224", "Realtek High Definition Audio", DeviceType.TypeSpeaker))
        devices.add(DeviceItem("59357639-6a43-4b79-8184-f79aed9a0dfc", "NVIDIA High Definition Audio", DeviceType.TypeSpeaker, True))
        return devices

    def active(self, deviceId):
        """激活指定的設備作為當前要用的設備"""
        self.__curDeviceId = deviceId

    def getCurDeviceId(self):
        return self.__curDeviceId


class DeviceUtil:
    """設備工具類"""

    def __init__(self):
        self.__mgrs = {}
        self.__mgrs[DeviceType.TypeSpeaker] = SpeakerMgr()
        # 為節省篇幅，MicrophoneMgr和CameraMgr不再實現
        # self.__microphoneMgr = MicrophoneMgr()
        # self.__cameraMgr = CameraMgr

    def __getDeviceMgr(self, type):
        return self.__mgrs[type]

    def getDeviceList(self, type):
        return self.__getDeviceMgr(type).enumerate()

    def active(self, type, deviceId):
        self.__getDeviceMgr(type).active(deviceId)

    def getCurDeviceId(self, type):
        return self.__getDeviceMgr(type).getCurDeviceId()


# Test
#=======================================================================================================================

def testRenting():
    myHome = HousingAgency("我愛我家")
    zhangsan = HouseOwner("張三");
    zhangsan.setHouseInfo("上地西里", 20, 2500, 1, "獨立衛生間", 0)
    zhangsan.publishHouseInfo(myHome)
    lisi = HouseOwner("李四")
    lisi.setHouseInfo("當代城市家園", 16, 1800, 1, "公用衛生間", 0)
    lisi.publishHouseInfo(myHome)
    wangwu = HouseOwner("王五")
    wangwu.setHouseInfo("金隅美和園", 18, 2600, 1, "獨立衛生間", 1)
    wangwu.publishHouseInfo(myHome)
    print()

    myHome.signContracts(3)
    print()

    tony = Customer("Tony")
    houseInfos = tony.findHouse("18平米左右，要有獨衛，要有窗戶，最好是朝南，有廚房更好！價位在2000左右", myHome)
    print()
    print("正在看房，尋找最合適的住巢……")
    print()
    AppropriateHouse = tony.seeHouse(houseInfos)
    tony.signContract(AppropriateHouse, myHome, 1)


def testDevices():
    deviceUtil = DeviceUtil()
    deviceList = deviceUtil.getDeviceList(DeviceType.TypeSpeaker)
    print("麥克風設備列表：")
    if deviceList.getCount() > 0:
        # 設置第一個設備為要用的設備
        deviceUtil.active(DeviceType.TypeSpeaker, deviceList.getByIdx(0).getId())
    for idx in range(0, deviceList.getCount()):
        device = deviceList.getByIdx(idx)
        print(device)
    print("當前使用的設備："
          + deviceList.getById(deviceUtil.getCurDeviceId(DeviceType.TypeSpeaker)).getName())


# testRenting()
testDevices()
