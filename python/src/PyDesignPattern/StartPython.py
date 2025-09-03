#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 11/21/2017

# Version 1.0
#=======================================================================================================================
def testDataType():
    age = 18        # int
    weight = 62.51  # float
    isAdult = True  # bool，只有True和False兩個枚舉值
    name = "Tony"   # string
    print("age:", age, " type:", type(age))
    print("weight:", weight, " type:", type(weight))
    print("isAdult:", isAdult, " type:", type(isAdult))
    print("name:", name, " type:", type(name))

    # 變量的類型可以直接改變
    age = name
    print("age:", age)

    a = b = c = 5
    # a,b,c三個變量指向相同的內存空間，具有相同的值
    print("a:", a, "b:", b, "c:", c)
    print("id(a):", id(a), "id(b):", id(b), "id(c):", id(c))


def testList():
    list1 = ['Thomson', 78, 12.58, 'Sunny', 180.2]
    list2 = [123, 'Tony']
    print("list1:", list1)  # 輸出完整列表
    print("list1[0]:", list1[0])  # 輸出列表的第一個元素
    print("list1[1:3]:", list1[1:3])  # 輸出第二個至第三個元素
    print("list1[2:]:", list1[2:])  # 輸出從第三個開始至列表末尾的所有元素
    print("list2 * 2 :", list2 * 2)  # 輸出列表兩次
    print("list1 + list2 :", list1 + list2)  # 打印組合的列表
    list1[1] = 100
    print("設置list[1]:", list1)  # 輸出完整列表
    list1.append("added data")
    print("list添加元素:", list1)  # 輸出增加後的列表


def testTuple():
    tp1 = ('Thomson', 78, 12.58, 'Sunny', 180.2)
    tp2 = (123, 'Tony')
    print("tp1:", tp1)  # 輸出完整元組
    print("tp2:", tp2)  # 輸出完整元組
    print("tp1[0]:", tp1[0])  # 輸出元組的第一個元素
    print("tp1[1:3]:", tp1[1:3])  # 輸出第二個至第三個的元素
    print("tp1[2:]:", tp1[2:])  # 輸出從第三個開始至列表末尾的所有元素
    print("tp2 * 2:", tp2 * 2)  # 輸出元組兩次
    print("tp1 + tp2:", tp1 + tp2)  # 打印組合的元組
    # tp1[1] = 100 # 不能修改元組內的元素


def testDictionary():
    dict1 = {}
    dict1['one'] = "This is one"
    dict1[2] = "This is two"
    dict2 = {'name': 'Tony', 'age': 24, 'height': 177}

    print("dict1:", dict1)
    print("dict1['one']:", dict1['one'])  # 輸出鍵為'one' 的值
    print("dict1[2]:", dict1[2])  # 輸出鍵為 2 的值
    print("dict2:", dict2) # 輸出完整的字典
    print("dict2.keys():", dict2.keys())  # 輸出所有鍵
    print("dict2.values():", dict2.values())  # 輸出所有值


def testSet():
    friuts = {"apple", "orange", "strawberry", "banana", "apple", "strawberry"}
    print("friuts:", friuts)
    print("type of friuts:", type(friuts))
    arr = [1, 2, 3, 4, 5, 1]
    numbers = set(arr)
    print("numbers:", numbers)
    friuts.add(1)
    print("numbers add 1:", numbers)

class Test:
    "這是一個測試類"

    def __init__(self):
        self.__ivalue = 5

    def getvalue(self):
        return self.__ivalue

def testClass():
    t = Test()
    print(t.getvalue())


class Person:
    "人"
    visited = 0

    def __init__(self, name, age, height):
        self.__name = name      # 私有成員，訪問權限為private
        self._age = age         # 保護成員，訪問權限為protected
        self.height = height    # 公有成員，訪問權限為public

    def getName(self):
        return self.__name

    def getAge(self):
        return self._age

    def showInfo(self):
        print("name:", self.__name)
        print("age:", self._age)
        print("height:", self.height)
        print("visited:", self.visited)
        Person.visited = Person.visited +1

class Teacher(Person):
    "老師"

    def __init__(self, name, age, height):
        super().__init__(name, age, height)
        self.__title = None

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title

    def showInfo(self):
        print("title:", self.__title)
        super().showInfo()


def testPerson():
    "測試方法"
    tony = Person("Tony", 25, 1.77)
    tony.showInfo()
    print()

    jenny = Teacher("Jenny", 34, 1.68)
    jenny.setTitle("教授")
    jenny.showInfo()


# testDataType()
testList()
# testTuple()
# testDictionary()
# testSet()
# testClass()

# testPerson()