#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 7/15/2018

# Version 1.0
#=======================================================================================================================
# class FilterScreen:
#     """過濾網"""
#
#     def doFilter(self, rawMaterials):
#         for material in rawMaterials:
#             if (material == "豆渣"):
#                 rawMaterials.remove(material)
#         return rawMaterials


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class Filter(metaclass=ABCMeta):
    """過濾器"""

    @abstractmethod
    def doFilter(self, elements):
        """過濾方法"""
        pass


class FilterChain(Filter):
    """過濾器鏈"""

    def __init__(self):
        self._filters = []

    def addFilter(self, filter):
        self._filters.append(filter)

    def removeFilter(self, filter):
        self._filters.remove(filter)

    def doFilter(self, elements):
        for filter in self._filters:
            elements = filter.doFilter(elements)
        return elements


# 基於框架的實現
#==============================
class FilterScreen(Filter):
    """過濾網"""

    def doFilter(self, elements):
        for material in elements:
            if (material == "豆渣"):
                elements.remove(material)
        return elements


import re
# 引入正則表達式庫

class SensitiveFilter(Filter):
    """敏感詞過濾"""

    def __init__(self):
        self.__sensitives = ["黃色", "臺獨", "貪汙"]

    def doFilter(self, elements):
        # 敏感詞列表轉換成正則表達式
        regex = ""
        for word in self.__sensitives:
            regex += word + "|"
        regex = regex[0: len(regex) - 1]

        # 對每個元素進行過濾
        newElements = []
        for element in elements:
            item, num = re.subn(regex, "", element)
            newElements.append(item)

        return newElements


class HtmlFilter(Filter):
    """HTML特殊字符轉換"""

    def __init__(self):
        self.__wordMap = {
            "&": "&amp;",
            "'": " &apos;",
            ">": "&gt;",
            "<": "&lt;",
            "\"": " &quot;",
        }

    def doFilter(self, elements):
        newElements = []
        for element in elements:
            for key, value in self.__wordMap.items():
                element = element.replace(key, value)
            newElements.append(element)
        return newElements


# Test
#=======================================================================================================================

def testFilterScreen():
    rawMaterials = ["豆漿", "豆渣"]
    print("過濾前：", rawMaterials)
    filter = FilterScreen()
    filteredMaterials = filter.doFilter(rawMaterials)
    print("過濾後：",filteredMaterials)



def testFilter():
    rawMaterials = ["豆漿", "豆渣"]
    print("過濾前：", rawMaterials)
    filteredMaterials = list(filter(lambda material: material == "豆漿", rawMaterials))
    print("過濾後：", filteredMaterials)

def isSoybeanMilk(material):
    return material == "豆漿"



def testFiltercontent():
    contents = [
        '有人出售黃色書：<黃情味道>',
        '有人企圖搞臺獨活動, ——"造謠諮詢"',
    ]
    print("過濾前的內容：", contents)
    filterChain = FilterChain()
    filterChain.addFilter(SensitiveFilter())
    filterChain.addFilter(HtmlFilter())
    newContents = filterChain.doFilter(contents)
    print("過濾後的內容：", newContents)


# testFilterScreen()
# testFilter()
testFiltercontent()
