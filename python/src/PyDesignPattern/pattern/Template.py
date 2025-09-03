#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 7/8/2018

# Version 1.0 代碼框架
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Template(metaclass=ABCMeta):
    """模板類(抽象類)"""

    @abstractmethod
    def stepOne(self):
        pass

    @abstractmethod
    def stepTwo(self):
        pass

    @abstractmethod
    def stepThree(self):
        pass

    def templateMethold(self):
        """模板方法"""
        self.stepOne()
        self.stepTwo()
        self.stepThree()


class TemplateImplA(Template):
    """模板實現類A"""

    def stepOne(self):
        print("步驟一")

    def stepTwo(self):
        print("步驟二")

    def stepThree(self):
        print("步驟三")


class TemplateImplB(Template):
    """模板實現類B"""

    def stepOne(self):
        print("Step one")

    def stepTwo(self):
        print("Step two")

    def stepThree(self):
        print("Step three")


# Version 2.0 閱讀器視圖
#=======================================================================================================================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class ReaderView(metaclass=ABCMeta):
    """閱讀器視圖"""

    def __init__(self):
        self.__curPageNum = 1

    def getPage(self, pageNum):
        self.__curPageNum = pageNum
        return "第" + str(pageNum) + "的內容"

    def prePage(self):
        """模板方法，往前翻一頁"""
        content = self.getPage(self.__curPageNum - 1)
        self._displayPage(content)

    def nextPage(self):
        """模板方法，往後翻一頁"""
        content = self.getPage(self.__curPageNum + 1)
        self._displayPage(content)

    @abstractmethod
    def _displayPage(self, content):
        """翻頁效果"""
        pass


class SmoothView(ReaderView):
    """左右平滑的視圖"""

    def _displayPage(self, content):
        print("左右平滑:" + content)


class SimulationView(ReaderView):
    """仿真翻頁的視圖"""

    def _displayPage(self, content):
        print("仿真翻頁:" + content)


# Test
#=======================================================================================================================
def testReader():
    smoothView = SmoothView()
    smoothView.nextPage()
    smoothView.prePage()

    simulationView = SimulationView()
    simulationView.nextPage()
    simulationView.prePage()

def testTemplate():
    templateA = TemplateImplA()
    templateA.templateMethold()
    templateB = TemplateImplB()
    templateB.templateMethold()


testReader()
# testTemplate()