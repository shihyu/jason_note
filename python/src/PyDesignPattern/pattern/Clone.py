#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 4/1/2018

# Version 1.0
#=======================================================================================================================
# from copy import copy, deepcopy
#
# class Person:
#     """人"""
#
#     def __init__(self, name, age):
#         self.__name = name
#         self.__age = age
#
#     def showMyself(self):
#         print("我是" + self.__name + ",年齡" + str(self.__age) + ".")
#
#     def coding(self):
#         print("我是碼農，我用程序改變世界，Coding...")
#
#     def reading(self):
#         print("閱讀使我快樂！知識使我成長！如飢似渴地閱讀是生活的一部分...")
#
#     def fallInLove(self):
#         print("春風吹，月亮明，花前月下好相約...")
#
#     def clone(self):
#         return copy(self)


# 淺拷貝與深拷貝
#=======================================================================================================================
from copy import copy, deepcopy

class PetStore:
    """寵物店"""

    def __init__(self, name):
        self.__name = name
        self.__petList = []

    def setName(self, name):
        self.__name = name

    def showMyself(self):
        print("%s 寵物店有以下寵物：" % self.__name)
        for pet in self.__petList:
            print(pet + "\t", end="")
        print()

    def addPet(self, pet):
        self.__petList.append(pet)


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from copy import copy, deepcopy

class Clone:
    """克隆的基類"""

    def clone(self):
        """淺拷貝的方式克隆對象"""
        return copy(self)

    def deepClone(self):
        """深拷貝的方式克隆對象"""
        return deepcopy(self)


# 基於框架的實現
#==============================
class Person(Clone):
    """人"""

    def __init__(self, name, age):
        self.__name = name
        self.__age = age

    def showMyself(self):
        print("我是" + self.__name + ",年齡" + str(self.__age) + ".")

    def coding(self):
        print("我是碼農，我用程序改變世界，Coding...")

    def reading(self):
        print("閱讀使我快樂！知識使我成長！如飢似渴地閱讀是生活的一部分...")

    def fallInLove(self):
        print("春風吹，月亮明，花前月下好相約...")


# 實戰應用
# =======================================================================================================================
class AppConfig(Clone):
    """應用程序功能配置"""

    def __init__(self, configName):
        self.__configName = configName
        self.parseFromFile("./config/default.xml")

    def parseFromFile(self, filePath):
        """
        從配置文件中解析配置項
        真實項目中通過會將配置保存到配置文件中，保證下次開啟時依然能夠生效；
        這裡為簡單起見，不從文件中讀取，以初始化的方式來模擬。
        """
        self.__fontType = "宋體"
        self.__fontSize = 14
        self.__language = "中文"
        self.__logPath = "./logs/appException.log"

    def saveToFile(self, filePath):
        """
        將配置保存到配置文件中
        這裡為簡單起見，不再實現
        """
        pass

    def copyConfig(self, configName):
        """創建一個配置的副本"""
        config = self.deepClone()
        config.__configName = configName
        return config

    def showInfo(self):
        print("%s 的配置信息如下：" % self.__configName)
        print("字體：", self.__fontType)
        print("字號：", self.__fontSize)
        print("語言：", self.__language)
        print("異常文件的路徑：", self.__logPath)

    def setFontType(self, fontType):
        self.__fontType = fontType

    def setFontSize(self, fontSize):
        self.__fontSize = fontSize

    def setLanguage(self, language):
        self.__language = language

    def setLogPath(self, logPath):
        self.__logPath = logPath


# Test
#=======================================================================================================================

def testClone():
    tony = Person("Tony", 27)
    tony.showMyself()
    tony.coding()

    tony1 = tony.clone()
    tony1.showMyself()
    tony1.reading()

    tony2 = tony.clone()
    tony2.showMyself()
    tony2.fallInLove()


def testPetStore():
    petter = PetStore("Petter")
    petter.addPet("小狗Coco")
    print("父本petter：", end="")
    petter.showMyself()
    print()

    petter1 = deepcopy(petter)
    petter1.addPet("小貓Amy")
    print("副本petter1：", end="")
    petter1.showMyself()
    print("父本petter：", end="")
    petter.showMyself()
    print()

    petter2 = copy(petter)
    petter2.addPet("小兔Ricky")
    print("副本petter2：", end="")
    petter2.showMyself()
    print("父本petter：", end="")
    petter.showMyself()


def testList():
    list = [1, 2, 3];
    list1 = list;
    print("id(list):", id(list))
    print("id(list1):", id(list1))
    print("修改之前：")
    print("list:", list)
    print("list1:", list1)
    list1.append(4);
    print("修改之後：")
    print("list:", list)
    print("list1:", list1)

    # petter = PetStore("Petter")
    # petter.addPet("小狗Coco")
    # print("父本tony：", end="")
    # petter.showMyself()
    #
    # petter1 = petter
    # petter1.addPet("小貓Amy")
    # print("副本tony1：", end="")
    # petter1.showMyself()
    # print("父本tony：", end="")
    # petter.showMyself()



def testAppConfig():
    defaultConfig = AppConfig("default")
    defaultConfig.showInfo()
    print()

    newConfig = defaultConfig.copyConfig("tonyConfig")
    newConfig.setFontType("雅黑")
    newConfig.setFontSize(18)
    newConfig.setLanguage("English")
    newConfig.showInfo()


# testClone()
# testPetStore()
# testList()
testAppConfig()