#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 4/24/2018

# Version 1.0
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class IHightPerson(metaclass=ABCMeta):
    """接口類，提供空實現的方法，由子類去實現"""

    @abstractmethod
    def getName(self):
        """獲取姓名"""
        pass

    @abstractmethod
    def getHeight(self):
        """獲取身高"""
        pass

    @abstractmethod
    def appearance(self, person):
        """外貌"""
        pass


class HighPerson(IHightPerson):
    """個高的人"""

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def getHeight(self):
        return 170

    def appearance(self):
        print(self.getName() + "身高" + str(self.getHeight()) + "，完美如你，天生的美女！")


class ShortPerson:
    """個矮的人"""

    def __init__(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def getRealHeight(self):
        return 160

    def getShoesHeight(self):
        return 6


class DecoratePerson(ShortPerson, IHightPerson):
    """有高跟鞋搭配的人"""

    def __init__(self, name):
        super().__init__(name)

    def getName(self):
        return super().getName()

    def getHeight(self):
        return super().getRealHeight() + super().getShoesHeight()

    def appearance(self):
        print(self.getName() + "身高" + str(self.getHeight()) + ", 在高跟鞋的適配下，你身高不輸高圓圓，氣質不輸范冰冰！")


class HeightMatch:
    """身高匹配"""

    def __init__(self, person):
        self.__person = person

    def matching(self, person1):
        """假設標準身高差為10釐米內"""
        distance = abs(self.__person.getHeight() - person1.getHeight())
        isMatch = distance <= 10
        print(self.__person.getName() + "和" + person1.getName() + "是否為情侶的標準身高差："
              + ("是" if isMatch else "否") + ", 差值：" + str(distance))


class Hotel:
    """(高級)酒店"""

    def recruit(self, person):
        """
        :param person: IHightPerson的對象
        """
        suitable = self.receptionistSuitable(person)
        print(person.getName() + "是否適合做接待員：", "符合" if suitable else "不符合")

    def receptionistSuitable(self, person):
        """
        是否可以成為(高級酒店)接待員
        :param person: IHightPerson的對象
        :return: 是否符合做接待員的條件
        """
        return person.getHeight() >= 165;

# Version 1.0
# =======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class SocketEntity:
    """接口類型定義"""

    def __init__(self, numOfPin, typeOfPin):
        self.__numOfPin = numOfPin
        self.__typeOfPin = typeOfPin

    def getNumOfPin(self):
        return self.__numOfPin

    def setNumOfPin(self, numOfPin):
        self.__numOfPin = numOfPin

    def getTypeOfPin(self):
        return self.__typeOfPin

    def setTypeOfPin(self, typeOfPin):
        self.__typeOfPin = typeOfPin


class ISocket(metaclass=ABCMeta):
    """插座類型"""

    def getName(self):
        """插座名稱"""
        pass

    def getSocket(self):
        """獲取接口"""
        pass


class ChineseSocket(ISocket):
    """國標插座"""

    def getName(self):
        return  "國標插座"

    def getSocket(self):
        return SocketEntity(3, "八字扁型")


class BritishSocket:
    """英標插座"""

    def name(self):
        return  "英標插座"

    def socketInterface(self):
        return SocketEntity(3, "T字方型")

class AdapterSocket(ISocket):
    """插座轉換器"""

    def __init__(self, britishSocket):
        self.__britishSocket = britishSocket

    def getName(self):
        return  self.__britishSocket.name() + "轉換器"

    def getSocket(self):
        socket = self.__britishSocket.socketInterface()
        socket.setTypeOfPin("八字扁型")
        return socket



# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Target(metaclass=ABCMeta):
    """目標類"""

    @abstractmethod
    def function(self):
        pass


class Adaptee:
    """源對象類"""

    def speciaficFunction(self):
        print("被適配對象的特殊功能")

class Adapter(Target):
    """適配器"""

    def __init__(self, adaptee):
        self.__adaptee = adaptee

    def function(self):
        print("進行功能的轉換")
        self.__adaptee.speciaficFunction()



# 基於框架的實現
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
import os
# 導入os庫,用於文件、路徑相關的解析

class Page:
    """電子書一頁的內容"""
    def __init__(self, pageNum):
        self.__pageNum = pageNum

    def getContent(self):
        return "第 " + str(self.__pageNum) + " 頁的內容..."


class Catalogue:
    """目錄結構"""

    def __init__(self, title):
        self.__title = title
        self.__chapters = []

    def addChapter(self, title):
        self.__chapters.append(title)

    def showInfo(self):
        print("書名：" + self.__title)
        print("目錄:")
        for chapter in self.__chapters:
            print("    " + chapter)


class IBook(metaclass=ABCMeta):
    """電子書文檔的接口類"""

    @abstractmethod
    def parseFile(self, filePath):
        """解析文檔"""
        pass

    @abstractmethod
    def getCatalogue(self):
        """獲取目錄"""
        pass

    @abstractmethod
    def getPageCount(self):
        """獲取頁數"""
        pass

    @abstractmethod
    def getPage(self, pageNum):
        """獲取第pageNum頁的內容"""
        pass


class TxtBook(IBook):
    """TXT解析類"""

    def parseFile(self, filePath):
        # 模擬文檔的解析
        print(filePath + " 文件解析成功")
        self.__title = os.path.splitext(filePath)[0]
        self.__pageCount = 500
        return True

    def getCatalogue(self):
        catalogue = Catalogue(self.__title)
        catalogue.addChapter("第一章 標題")
        catalogue.addChapter("第二章 標題")
        return catalogue

    def getPageCount(self):
        return self.__pageCount

    def getPage(self, pageNum):
        return Page(pageNum)


class EpubBook(IBook):
    """Epub解析類"""

    def parseFile(self, filePath):
        # 模擬文檔的解析
        print(filePath + " 文件解析成功")
        self.__title = os.path.splitext(filePath)[0]
        self.__pageCount = 800
        return True

    def getCatalogue(self):
        catalogue = Catalogue(self.__title)
        catalogue.addChapter("第一章 標題")
        catalogue.addChapter("第二章 標題")
        return catalogue

    def getPageCount(self):
        return self.__pageCount

    def getPage(self, pageNum):
        return Page(pageNum)


class Outline:
    """第三方PDF解析庫的目錄類"""
    def __init__(self):
        self.__outlines = []

    def addOutline(self, title):
        self.__outlines.append(title)

    def getOutlines(self):
        return self.__outlines


class PdfPage:
    "PDF頁"

    def __init__(self, pageNum):
        self.__pageNum = pageNum

    def getPageNum(self):
        return self.__pageNum


class ThirdPdf:
    """第三方PDF解析庫"""

    def __init__(self):
        self.__pageSize = 0
        self.__title = ""

    def open(self, filePath):
        print("第三方庫解析PDF文件：" + filePath)
        self.__title = os.path.splitext(filePath)[0]
        self.__pageSize = 1000
        return True

    def getTitle(self):
        return self.__title

    def getOutline(self):
        outline = Outline()
        outline.addOutline("第一章 PDF電子書標題")
        outline.addOutline("第二章 PDF電子書標題")
        return outline

    def pageSize(self):
        return self.__pageSize

    def page(self, index):
        return PdfPage(index)


class PdfAdapterBook(ThirdPdf, IBook):
    """對第三方的PDF解析庫重新進行包裝"""

    def __init__(self, thirdPdf):
        self.__thirdPdf = thirdPdf

    def parseFile(self, filePath):
        # 模擬文檔的解析
        rtn = self.__thirdPdf.open(filePath)
        if(rtn):
            print(filePath + "文件解析成功")
        return rtn

    def getCatalogue(self):
        outline = self.getOutline()
        print("將Outline結構的目錄轉換成Catalogue結構的目錄")
        catalogue = Catalogue(self.__thirdPdf.getTitle())
        for title in outline.getOutlines():
            catalogue.addChapter(title)
        return catalogue

    def getPageCount(self):
        return self.__thirdPdf.pageSize()

    def getPage(self, pageNum):
        page = self.page(pageNum)
        print("將PdfPage的面對象轉換成Page的對象")
        return Page(page.getPageNum())


class Reader:
    "閱讀器"

    def __init__(self, name):
        self.__name = name
        self.__filePath = ""
        self.__curBook = None
        self.__curPageNum = -1

    def __initBook(self, filePath):
        self.__filePath = filePath
        extName = os.path.splitext(filePath)[1]
        if(extName.lower() == ".epub"):
            self.__curBook = EpubBook()
        elif(extName.lower() == ".txt"):
            self.__curBook = TxtBook()
        elif(extName.lower() == ".pdf"):
            self.__curBook = PdfAdapterBook(ThirdPdf())
        else:
            self.__curBook = None

    def openFile(self, filePath):
        self.__initBook(filePath)
        if(self.__curBook is not None):
            rtn = self.__curBook.parseFile(filePath)
            if(rtn):
                self.__curPageNum = 1
            return rtn
        return False

    def closeFile(self):
        print("關閉 " + self.__filePath + " 文件")
        return True

    def showCatalogue(self):
        catalogue = self.__curBook.getCatalogue()
        catalogue.showInfo()

    def prePage(self):
        print("往前翻一頁：", end="")
        return self.gotoPage(self.__curPageNum - 1)

    def nextPage(self):
        print("往後翻一頁：", end="")
        return self.gotoPage(self.__curPageNum + 1)

    def gotoPage(self, pageNum):
        if(pageNum > 1 and pageNum < self.__curBook.getPageCount() -1):
            self.__curPageNum = pageNum

        print("顯示第" + str(self.__curPageNum) + "頁")
        page = self.__curBook.getPage(self.__curPageNum)
        page.getContent()
        return page


# Test
#=======================================================================================================================

def testPerson():
    lira = HighPerson("Lira")
    lira.appearance()
    demi = DecoratePerson("Demi");
    demi.appearance()

    haigerMatching = HeightMatch(HighPerson("Haiger"))
    haigerMatching.matching(lira)
    haigerMatching.matching(demi)
    # hotel = Hotel()
    # hotel.recruit(lira)
    # hotel.recruit(demi)

def testAdapter():
    adpater = Adapter(Adaptee())
    adpater.function()

def testReader():
    reader = Reader("閱讀器")
    if(not reader.openFile("平凡的世界.txt")):
        return
    reader.showCatalogue()
    reader.prePage()
    reader.nextPage()
    reader.nextPage()
    reader.closeFile()
    print()

    if (not reader.openFile("追風箏的人.epub")):
        return
    reader.showCatalogue()
    reader.nextPage()
    reader.nextPage()
    reader.prePage()
    reader.closeFile()
    print()

    if (not reader.openFile("如何從生活中領悟設計模式.pdf")):
        return
    reader.showCatalogue()
    reader.nextPage()
    reader.nextPage()
    reader.closeFile()


def canChargeforDigtalDevice(name, socket):
    if socket.getNumOfPin() == 3 and socket.getTypeOfPin() == "八字扁型":
        isStandard = "符合"
        canCharge = "可以"
    else:
        isStandard = "不符合"
        canCharge = "不能"

    print("[%s]：\n針腳數量：%d，針腳類型：%s； %s中國標準，%s給大陸的電子設備充電！"
          % (name, socket.getNumOfPin(), socket.getTypeOfPin(), isStandard, canCharge))

def testSocket():
    chineseSocket = ChineseSocket()
    canChargeforDigtalDevice(chineseSocket.getName(), chineseSocket.getSocket())

    britishSocket = BritishSocket()
    canChargeforDigtalDevice(britishSocket.name(), britishSocket.socketInterface())

    adapterSocket = AdapterSocket(britishSocket)
    canChargeforDigtalDevice(adapterSocket.getName(), adapterSocket.getSocket())


# testPerson()
# testAdapter()
testReader()
# testSocket()