#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 12/16/2017

# Version 1.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class ComputerComponent(metaclass=ABCMeta):
    """組件，所有子配件的基類"""

    def __init__(self, name):
        self._name = name

    @abstractmethod
    def showInfo(self, indent = ""):
        pass

    def isComposite(self):
        return False

    def startup(self, indent = ""):
        print("%s%s 準備開始工作..." % (indent, self._name) )

    def shutdown(self, indent = ""):
        print("%s%s 即將結束工作..." % (indent, self._name) )


class CPU(ComputerComponent):
    """中央處理器"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%sCPU:%s,可以進行高速計算。" % (indent, self._name))


class MemoryCard(ComputerComponent):
    """內存條"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s內存:%s,可以緩存數據，讀寫速度快。" % (indent, self._name))


class HardDisk(ComputerComponent):
    """硬盤"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s硬盤:%s,可以永久存儲數據，容量大。" % (indent, self._name) )


class GraphicsCard(ComputerComponent):
    """顯卡"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s顯卡:%s,可以高速計算和處理圖形圖像。" % (indent, self._name) )


class Battery(ComputerComponent):
    """電源"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s電源:%s,可以持續給主板和外接配件供電。" % (indent, self._name) )


class Fan(ComputerComponent):
    """風扇"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s風扇:%s，輔助CPU散熱。" % (indent, self._name) )


class Displayer(ComputerComponent):
    """"顯示器"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print("%s顯示器:%s，負責內容的顯示。" % (indent, self._name) )


class ComputerComposite(ComputerComponent):
    """配件組合器"""

    def __init__(self, name):
        super().__init__(name)
        self._components = []

    def showInfo(self, indent):
        print("%s,由以下部件組成:" % (self._name) )
        indent += "\t"
        for element in self._components:
            element.showInfo(indent)

    def isComposite(self):
        return True

    def addComponent(self, component):
        self._components.append(component)

    def removeComponent(self, component):
        self._components.remove(component)

    def startup(self, indent):
        super().startup(indent)
        indent += "\t"
        for element in self._components:
            element.startup(indent)

    def shutdown(self, indent):
        super().shutdown(indent)
        indent += "\t"
        for element in self._components:
            element.shutdown(indent)


class Mainboard(ComputerComposite):
    """主板"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print(indent + "主板:", end="")
        super().showInfo(indent)


class ComputerCase(ComputerComposite):
    """機箱"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print(indent + "機箱:", end="")
        super().showInfo(indent)


class Computer(ComputerComposite):
    """電腦"""

    def __init__(self, name):
        super().__init__(name)

    def showInfo(self, indent):
        print(indent + "電腦:", end="")
        super().showInfo(indent)


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================

from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Component(metaclass=ABCMeta):
    """組件"""

    def __init__(self, name):
        self._name = name

    def getName(self):
        return self._name

    def isComposite(self):
        return False

    @abstractmethod
    def feature(self, indent):
        # indent 僅用於內容輸出時的縮進
        pass

class Composite(Component):
    """複合組件"""

    def __init__(self, name):
        super().__init__(name)
        self._components = []

    def addComponent(self, component):
        self._components.append(component)

    def removeComponent(self, component):
        self._components.remove(component)

    def isComposite(self):
        return True

    def feature(self, indent):
        indent += "\t"
        for component in self._components:
            print(indent, end="")
            component.feature(indent)



class ComponentImplA(Component):
    "Test"

    def __init__(self, name):
        super().__init__(name)

    def feature(self):
        print("name：%s" % self._name)


# 基於框架的實現
#==============================
import os
# 引入 os 模塊

class FileDetail(Component):
    """誶詳情"""
    def __init__(self, name):
        super().__init__(name)
        self._size = 0

    def setSize(self, size):
        self._size = size

    def getFileSize(self):
        return self._size

    def feature(self, indent):
        # 文件大小，單位：KB，精確度：2位小數
        fileSize = round(self._size / float(1024), 2)
        print("文件名稱：%s， 文件大小：%sKB" % (self._name, fileSize) )


class FolderDetail(Composite):
    """文件夾詳情"""

    def __init__(self, name):
        super().__init__(name)
        self._count = 0

    def setCount(self, fileNum):
        self._count = fileNum

    def getCount(self):
        return self._count

    def feature(self, indent):
        print("文件夾名：%s， 文件數量：%d。包含的文件：" % (self._name, self._count) )
        super().feature(indent)


def scanDir(rootPath, folderDetail):
    """掃描某一文件夾下的所有目錄"""
    if not os.path.isdir(rootPath):
        raise ValueError("rootPath不是有效的路徑：%s" % rootPath)

    if folderDetail is None:
        raise ValueError("folderDetail不能為空!")


    fileNames = os.listdir(rootPath)
    for fileName in fileNames:
        filePath = os.path.join(rootPath, fileName)
        if os.path.isdir(filePath):
            folder = FolderDetail(fileName)
            scanDir(filePath, folder)
            folderDetail.addComponent(folder)
        else:
            fileDetail = FileDetail(fileName)
            fileDetail.setSize(os.path.getsize(filePath))
            folderDetail.addComponent(fileDetail)
            folderDetail.setCount(folderDetail.getCount() + 1)



# Test
#=======================================================================================================================
def testComputer():
    mainBoard = Mainboard("GIGABYTE Z170M M-ATX")
    mainBoard.addComponent(CPU("Intel Core i5-6600K"))
    mainBoard.addComponent(MemoryCard("Kingston Fury DDR4"))
    mainBoard.addComponent(HardDisk("Kingston V300 "))
    mainBoard.addComponent(GraphicsCard("Colorful iGame750"))

    computerCase = ComputerCase("SAMA MATX")
    computerCase.addComponent(mainBoard)
    computerCase.addComponent(Battery("Antec VP 450P"))
    computerCase.addComponent(Fan("DEEPCOOL 120T"))

    computer = Computer("Tony DIY電腦")
    computer.addComponent(computerCase)
    computer.addComponent(Displayer("AOC LV243XIP"))

    computer.showInfo("")
    print("\n開機過程:")
    computer.startup("")
    print("\n關機過程:")
    computer.shutdown("")


def testComposite():
    tony = ComponentImplA("Tony")
    tony.feature()
    karry = ComponentImplA("Karry")
    composite = Composite("Composite")
    composite.addComponent(tony)
    composite.addComponent(karry)
    composite.feature()


def testDir():
    folder = FolderDetail("生活中的設計模式")
    scanDir("E:\生活中的設計模式", folder)
    folder.feature("")

    # isDir = os.path.isfile("D:\Test\file1.txt")
    # print(isDir)

# testComputer()
# testComposite()
testDir()