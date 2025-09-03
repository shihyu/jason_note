#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 6/30/2018

# Version 1.0
#=======================================================================================================================
# from abc import ABCMeta, abstractmethod
# # 引入ABCMeta和abstractmethod來定義抽象類和抽象方法
#
# class DesignPatternBook:
#     """《從生活的角度解讀設計模式》一書"""
#     def getName(self):
#         return "《從生活的角度解讀設計模式》"
#
#
# class Reader(metaclass=ABCMeta):
#     """訪問者，也就是讀者"""
#
#     @abstractmethod
#     def read(self, book):
#         pass
#
# class Engineer(Reader):
#     """工程師"""
#
#     def read(self, book):
#         print("技術狗讀%s一書後的感受：能抓住模式的核心思想，深入淺出，很有見地！" % book.getName())
#
#
# class ProductManager(Reader):
#     """產品經理"""
#
#     def read(self, book):
#         print("產品經理讀%s一書後的感受：配圖非常有趣，文章很有層次感！" % book.getName())
#
# class OtherFriend(Reader):
#     """IT圈外的朋友"""
#
#     def read(self, book):
#         print("IT圈外的朋友讀%s一書後的感受：技術的內容一臉懵逼，但故事很精彩，像是看小說或是故事集！"
#               % book.getName())

# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from abc import ABCMeta, abstractmethod
# 引入ABCMeta和abstractmethod來定義抽象類和抽象方法

class DataNode(metaclass=ABCMeta):
    """數據結構類"""

    def accept(self, visitor):
        """接受訪問者的訪問"""
        visitor.visit(self)

class Visitor(metaclass=ABCMeta):
    """訪問者"""

    @abstractmethod
    def visit(self, data):
        """對數據對象的訪問操作"""
        pass


class ObjectStructure:
    """數據結構的管理類，也是數據對象的一個容器，可遍歷容器內的所有元素"""

    def __init__(self):
        self.__datas = []

    def add(self, dataElement):
        self.__datas.append(dataElement)

    def action(self, visitor):
        """進行數據訪問的操作"""
        for data in self.__datas:
            data.accept(visitor)


# 基於框架的實現
#==============================
class DesignPatternBook(DataNode):
    """《從生活的角度解讀設計模式》一書"""

    def getName(self):
        return "《從生活的角度解讀設計模式》"


class Engineer(Visitor):
    """工程師"""

    def visit(self, book):
        print("技術狗讀%s一書後的感受：能抓住模式的核心思想，深入淺出，很有見地！" % book.getName())


class ProductManager(Visitor):
    """產品經理"""

    def visit(self, book):
        print("產品經理讀%s一書後的感受：配圖非常有趣，文章很有層次感！" % book.getName())


class OtherFriend(Visitor):
    """IT圈外的朋友"""

    def visit(self, book):
        print("IT圈外的朋友讀%s一書後的感受：技術的內容一臉懵逼，但故事很精彩，像是看小說或是故事集！"
              % book.getName())


# 實戰
# =======================================================================================================================
class Animal(DataNode):
    """動物類"""

    def __init__(self, name, isMale, age, weight):
        self.__name = name
        self.__isMale = isMale
        self.__age = age
        self.__weight = weight

    def getName(self):
        return self.__name

    def isMale(self):
        return self.__isMale

    def getAge(self):
        return self.__age

    def getWeight(self):
        return self.__weight

class Cat(Animal):
    """貓"""

    def __init__(self, name, isMale, age, weight):
        super().__init__(name, isMale, age, weight)

    def speak(self):
        print("miao~")


class Dog(Animal):
    """狗"""

    def __init__(self,  name, isMale, age, weight):
        super().__init__( name, isMale, age, weight)

    def speak(self):
        print("wang~")


class GenderCounter(Visitor):
    """性別統計"""

    def __init__(self):
        self.__maleCat = 0
        self.__femaleCat = 0
        self.__maleDog = 0
        self.__femalDog = 0

    def visit(self, data):
        if isinstance(data, Cat):
            if data.isMale():
                self.__maleCat += 1
            else:
                self.__femaleCat += 1
        elif isinstance(data, Dog):
            if data.isMale():
                self.__maleDog += 1
            else:
                self.__femalDog += 1
        else:
            print("Not support this type")

    def getInfo(self):
        print("%d只雄貓，%d只雌貓，%d只雄狗，%d只雌狗。"
              % (self.__maleCat, self.__femaleCat, self.__maleDog, self.__femalDog) )


class WeightCounter(Visitor):
    """體重的統計"""

    def __init__(self):
        self.__catNum = 0
        self.__catWeight = 0
        self.__dogNum = 0
        self.__dogWeight  = 0

    def visit(self, data):
        if isinstance(data, Cat):
            self.__catNum +=1
            self.__catWeight += data.getWeight()
        elif isinstance(data, Dog):
            self.__dogNum += 1
            self.__dogWeight += data.getWeight()
        else:
            print("Not support this type")

    def getInfo(self):
        print("貓的平均體重是：%0.2fkg， 狗的平均體重是：%0.2fkg" %
              ((self.__catWeight / self.__catNum),(self.__dogWeight / self.__dogNum)))


class AgeCounter(Visitor):
    """年齡統計"""

    def __init__(self):
        self.__catMaxAge = 0
        self.__dogMaxAge = 0

    def visit(self, data):
        if isinstance(data, Cat):
            if self.__catMaxAge < data.getAge():
                self.__catMaxAge = data.getAge()
        elif isinstance(data, Dog):
            if self.__dogMaxAge < data.getAge():
                self.__dogMaxAge = data.getAge()
        else:
            print("Not support this type")

    def getInfo(self):
        print("貓的最大年齡是：%s，狗的最大年齡是：%s" % (self.__catMaxAge, self.__dogMaxAge) )

# Test
#=======================================================================================================================

def testBook():
    book = DesignPatternBook()
    fans = [Engineer(), ProductManager(), OtherFriend()];
    for fan in fans:
        fan.read(book)

def testVisitBook():
    book = DesignPatternBook()
    objMgr = ObjectStructure()
    objMgr.add(book)
    objMgr.action(Engineer())
    objMgr.action(ProductManager())
    objMgr.action(OtherFriend())


def testAnimal():
    animals = ObjectStructure()
    animals.add(Cat("Cat1", True, 1, 5))
    animals.add(Cat("Cat2", False, 0.5, 3))
    animals.add(Cat("Cat3", False, 1.2, 4.2))
    animals.add(Dog("Dog1", True, 0.5, 8))
    animals.add(Dog("Dog2", True, 3, 52))
    animals.add(Dog("Dog3", False, 1, 21))
    animals.add(Dog("Dog4", False, 2, 25))
    genderCounter = GenderCounter()
    animals.action(genderCounter)
    genderCounter.getInfo()
    print()

    weightCounter = WeightCounter()
    animals.action(weightCounter)
    weightCounter.getInfo()
    print()

    ageCounter = AgeCounter()
    animals.action(ageCounter)
    ageCounter.getInfo()


# testBook()
# testVisitBook()
testAnimal()