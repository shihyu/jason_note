#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 7/21/2018

# Version 1.0
#=======================================================================================================================

class Employee:
    """公司員工"""

    def __init__(self, name):
        self.__name = name

    def doPerformance(self, skill):
        print(self.__name + "的表演:", end="")
        skill()


def sing():
    """唱歌"""
    print("唱一首歌")

def dling():
    """拉Ukulele"""
    print("拉一曲Ukulele")

def joke():
    """說段子"""
    print("說一搞笑段子")

def performMagicTricks():
    """表演魔術"""
    print("神祕魔術")

def skateboarding():
    """玩滑板"""
    print("酷炫滑板")


# Version 2.0
#=======================================================================================================================
# 代碼框架1：面向過程的實現方式
#==============================
def callback(*args, **kwargs):
    """回調函數"""
    # todo 函數體的實現


def otherFun(fun, *args, **kwargs):
    """高階函數，也叫包含函數"""
    # todo 函數體的實現

# 函數的調用方式
otherFun(callable)


# 代碼框架2：面向對象的實現方式
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Strategy(metaclass=ABCMeta):
    """算法的抽象類"""

    @abstractmethod
    def algorithm(self, *args, **kwargs):
        """定義算法"""
        pass

class StrategyA(Strategy):
    """策略A"""

    def algorithm(self, *args, **kwargs):
        print("算法A的實現...")

class StrategyB(Strategy):
    """策略B"""

    def algorithm(self, *args, **kwargs):
        print("算法B的實現...")

class Context:
    """上下文環境類"""

    def interface(self, strategy, *args, **kwargs):
        """交互接口"""
        print("回調執行前的操作")
        strategy.algorithm()
        print("回調執行後的操作")

# # 調用方式
# context = Context()
# context.interface(StrategyA())
# context.interface(StrategyB())


# 基於框架的實現1
#==============================
def isEvenNumber(num):
    return num % 2 == 0

def isGreaterThanTen(num):
    return num > 10

def getResultNumbers(fun, elements):
    newList = []
    for item in elements:
        if (fun(item)):
            newList.append(item)
    return newList


# 基於框架的實現2
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Skill(metaclass=ABCMeta):
    """技能的抽象類"""

    @abstractmethod
    def performance(self):
        """技能表演"""
        pass

class NewEmployee:
    """公司新員工"""

    def __init__(self, name):
        self.__name = name

    def doPerformance(self, skill):
        print(self.__name + "的表演:", end="")
        skill.performance()

class Sing(Skill):
    """唱歌"""
    def performance(self):
        print("唱一首歌")

class Joke(Skill):
    """說段子"""
    def performance(self):
        print("說一搞笑段子")

class Dling(Skill):
    """拉Ukulele"""
    def performance(self):
        print("拉一曲Ukulele")

class PerformMagicTricks(Skill):
    """表演魔術"""
    def performance(self):
        print("神祕魔術")

class Skateboarding(Skill):
    """玩滑板"""
    def performance(self):
        print("酷炫滑板")


# 回調在異步中的應用
# =======================================================================================================================
import requests
# 引入Http請求模塊
from threading import Thread
# 引入線程模塊

class DownloadThread (Thread):
    """下載文件的線程"""

    # 每次寫文件的緩衝大小
    CHUNK_SIZE = 1024 * 512

    def __init__(self, fileName, url, savePath, callBackProgerss, callBackFinished):
        super().__init__()
        self.__fileName = fileName
        self.__url = url
        self.__savePath = savePath
        self.__callbackProgress = callBackProgerss
        self.__callBackFionished = callBackFinished

    def run(self):
        readSize = 0
        r = requests.get(self.__url, stream=True)
        totalSize = int(r.headers.get('Content-Length'))
        print("[下載%s] 文件大小:%d" % (self.__fileName, totalSize))
        with open(self.__savePath, "wb") as file:
            for chunk in r.iter_content(chunk_size = self.CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    readSize += self.CHUNK_SIZE
                    self.__callbackProgress(self.__fileName, readSize, totalSize)
        self.__callBackFionished(self.__fileName)



# Test
#=======================================================================================================================

def testSkill():
    helen = Employee("Helen")
    helen.doPerformance(sing)
    frank = Employee("Frank")
    frank.doPerformance(dling)
    jacky = Employee("Jacky")
    jacky.doPerformance(joke)
    chork = Employee("Chork")
    chork.doPerformance(performMagicTricks)
    Kerry = Employee("Kerry")
    Kerry.doPerformance(skateboarding)

def testStrategySkill():
    helen = NewEmployee("Helen")
    helen.doPerformance(Sing())
    frank = NewEmployee("Frank")
    frank.doPerformance(Dling())
    jacky = NewEmployee("Jacky")
    jacky.doPerformance(Joke())
    chork = NewEmployee("Chork")
    chork.doPerformance(PerformMagicTricks())
    Kerry = NewEmployee("Kerry")
    Kerry.doPerformance(Skateboarding())


def testCallback():
    elements = [2, 3, 6, 9, 12, 15, 18]
    list1 = getResultNumbers(isEvenNumber, elements)
    list2 = getResultNumbers(isGreaterThanTen, elements)
    print("所有的偶數：", list1)
    print("大於10的數：", list2)

def testFilter():
    elements = [2, 3, 6, 9, 12, 15, 18]
    list1 = list(filter(lambda x: x % 2 == 0, elements))
    list2 = list(filter(lambda x: x > 10, elements))
    print("所有的偶數：", list1)
    print("大於10的數：", list2)




def testDownload():
    def downloadProgress(fileName, readSize, totalSize):
        """定義下載進度的回調函數"""
        percent = (readSize / totalSize) * 100
        print("[下載%s] 下載進度:%.2f%%" % (fileName, percent))

    def downloadFinished(fileName):
        """定義下載完成後的回調函數"""
        print("[下載%s] 文件下載完成！" % fileName)

    print("開始下載TestForDownload1.pdf......")
    downloadUrl1 = "http://pe9hg91q8.bkt.clouddn.com/TestForDownload1.pdf"
    download1 = DownloadThread("TestForDownload1", downloadUrl1, "./download/TestForDownload1.pdf", downloadProgress,
                               downloadFinished)
    download1.start()
    print("開始下載TestForDownload2.zip......")
    downloadUrl2 = "http://pe9hg91q8.bkt.clouddn.com/TestForDownload2.zip"
    download2 = DownloadThread("TestForDownload2", downloadUrl2, "./download/TestForDownload2.zip", downloadProgress,
                               downloadFinished)
    download2.start()
    print("執行其它的任務......")


# testSkill()
# testStrategySkill()
# testCallback()
# testFilter()


testDownload()
