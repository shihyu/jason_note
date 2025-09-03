#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 6/23/2018

# Version 1.0
#=======================================================================================================================
class Register:
    """報到登記"""

    def register(self, name):
        print("活動中心:%s同學報到成功！" % name)


class Payment:
    """繳費中心"""

    def pay(self, name, money):
        print("繳費中心:收到%s同學%s元付款，繳費成功！" % (name, money) )


class DormitoryManagementCenter:
    """生活中心(宿舍管理中心)"""

    def provideLivingGoods(self, name):
        print("生活中心:%s同學的生活用品已發放。" % name)


class Dormitory:
    """宿舍"""

    def meetRoommate(self, name):
        print("宿    舍:" + "大家好！這是剛來的%s同學，是你們未來需要共度四年的室友！相互認識一下……" % name)


class Volunteer:
    """迎新志願者"""

    def __init__(self, name):
        self.__name = name
        self.__register = Register()
        self.__payment = Payment()
        self.__lifeCenter = DormitoryManagementCenter()
        self.__dormintory = Dormitory()

    def welcomeFreshmen(self, name):
        print("你好,%s同學! 我是新生報到的志願者%s，我將帶你完成整個報到流程。" % (name, self.__name))
        self.__register.register(name)
        self.__payment.pay(name, 10000)
        self.__lifeCenter.provideLivingGoods(name)
        self.__dormintory.meetRoommate(name)


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================


# 基於框架的實現
#==============================
from os import path
# 引入path，進行路徑相關的處理
import logging
# 引入logging，進行錯誤時的日誌記錄

class ZIPModel:
    """ZIP模塊，負責ZIP文件的壓縮與解壓
    這裡只進行簡單模擬，不進行具體的解壓縮邏輯"""

    def compress(self, srcFilePath, dstFilePath):
        print("ZIP模塊正在進行“%s”文件的壓縮......" % srcFilePath)
        print("文件壓縮成功，已保存至“%s”" % dstFilePath)

    def decompress(self, srcFilePath, dstFilePath):
        print("ZIP模塊正在進行“%s”文件的解壓......" % srcFilePath)
        print("文件解壓成功，已保存至“%s”" % dstFilePath)


class RARModel:
    """RAR模塊，負責RAR文件的壓縮與解壓
    這裡只進行簡單模擬，不進行具體的解壓縮邏輯"""

    def compress(self, srcFilePath, dstFilePath):
        print("RAR模塊正在進行“%s”文件的壓縮......" % srcFilePath)
        print("文件壓縮成功，已保存至“%s”" % dstFilePath)

    def decompress(self, srcFilePath, dstFilePath):
        print("RAR模塊正在進行“%s”文件的解壓......" % srcFilePath)
        print("文件解壓成功，已保存至“%s”" % dstFilePath)


class ZModel:
    """7Z模塊，負責7Z文件的壓縮與解壓
    這裡只進行簡單模擬，不進行具體的解壓縮邏輯"""

    def compress(self, srcFilePath, dstFilePath):
        print("7Z模塊正在進行“%s”文件的壓縮......" % srcFilePath)
        print("文件壓縮成功，已保存至“%s”" % dstFilePath)

    def decompress(self, srcFilePath, dstFilePath):
        print("7Z模塊正在進行“%s”文件的解壓......" % srcFilePath)
        print("文件解壓成功，已保存至“%s”" % dstFilePath)


class CompressionFacade:
    """壓縮系統的外觀類"""

    def __init__(self):
        self.__zipModel = ZIPModel()
        self.__rarModel = RARModel()
        self.__zModel = ZModel()

    def compress(self, srcFilePath, dstFilePath, type):
        """根據不同的壓縮類型，壓縮成不同的格式"""
        # 獲取新的文件名
        extName = "." + type
        fullName = dstFilePath + extName
        if (type.lower() == "zip") :
            self.__zipModel.compress(srcFilePath, fullName)
        elif(type.lower() == "rar"):
            self.__rarModel.compress(srcFilePath, fullName)
        elif(type.lower() == "7z"):
            self.__zModel.compress(srcFilePath, fullName)
        else:
            logging.error("Not support this format:" + str(type))
            return False
        return True

    def decompress(self, srcFilePath, dstFilePath):
        """從srcFilePath中獲取後綴，根據不同的後綴名(拓展名)，進行不同格式的解壓"""
        baseName = path.basename(srcFilePath)
        extName = baseName.split(".")[1]
        if (extName.lower() == "zip") :
            self.__zipModel.decompress(srcFilePath, dstFilePath)
        elif(extName.lower() == "rar"):
            self.__rarModel.decompress(srcFilePath, dstFilePath)
        elif(extName.lower() == "7z"):
            self.__zModel.decompress(srcFilePath, dstFilePath)
        else:
            logging.error("Not support this format:" + str(extName))
            return False
        return True


# Test
#=======================================================================================================================
def testRegister():
    volunteer = Volunteer("Frank")
    volunteer.welcomeFreshmen("Tony")


def testCompression():
    facade = CompressionFacade()
    facade.compress("E:\標準文件\生活中的外觀模式.md",
                    "E:\壓縮文件\生活中的外觀模式", "zip")
    facade.decompress("E:\壓縮文件\生活中的外觀模式.zip",
                      "E:\標準文件\生活中的外觀模式.md")
    print()

    facade.compress("E:\標準文件\Python編程——從入門到實踐.pdf",
                    "E:\壓縮文件\Python編程——從入門到實踐", "rar")
    facade.decompress("E:\壓縮文件\Python編程——從入門到實踐.rar",
                      "E:\標準文件\Python編程——從入門到實踐.pdf")
    print()

    facade.compress("E:\標準文件\談談我對項目重構的看法.doc",
                    "E:\壓縮文件\談談我對項目重構的看法", "7z")
    facade.decompress("E:\壓縮文件\談談我對項目重構的看法.7z",
                      "E:\標準文件\談談我對項目重構的看法.doc")
    print()


def testPath():
    filePath = "E:\解析文件\生活中的外觀模式——學妹別慌，學長幫你.md"
    dirName = path.dirname(filePath)
    baseName = path.basename(filePath)
    fileName, extName = baseName.split('.')
    fullName = path.join(dirName, fileName + extName)
    i = 0


# testRegister()
testCompression()
# testPath()