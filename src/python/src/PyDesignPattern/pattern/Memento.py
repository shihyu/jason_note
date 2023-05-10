#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 5/19/2018

# Version 1.0
#=======================================================================================================================
class Engineer:
    """工程師"""

    def __init__(self, name):
        self.__name = name
        self.__workItems = []

    def addWorkItem(self, item):
        self.__workItems.append(item)

    def forget(self):
        self.__workItems.clear()
        print(self.__name + "工作太忙了，都忘記要做什麼了！")

    def writeTodoList(self):
        """將工作項記錄TodoList"""
        todoList = TodoList()
        for item in self.__workItems:
            todoList.writeWorkItem(item)
        return todoList

    def retrospect(self, todoList):
        """回憶工作項"""
        self.__workItems = todoList.getWorkItems()
        print(self.__name + "想起要做什麼了！")

    def showWorkItem(self):
        if(len(self.__workItems)):
            print(self.__name + "的工作項：")
            for idx in range(0, len(self.__workItems)):
                print(str(idx + 1) + ". " + self.__workItems[idx] + ";")
        else:
            print(self.__name + "暫無工作項！")


class TodoList:
    """工作項"""

    def __init__(self):
        self.__workItems = []

    def writeWorkItem(self, item):
        self.__workItems.append(item)

    def getWorkItems(self):
        return self.__workItems


class TodoListCaretaker:
    """TodoList管理類"""

    def __init__(self):
        self.__todoList = None

    def setTodoList(self, todoList):
        self.__todoList = todoList

    def getTodoList(self):
        return self.__todoList


# Version 2.0
#=======================================================================================================================
# 代碼框架
#==============================
from copy import deepcopy

class Memento:
    """備忘錄"""

    def setAttributes(self, dict):
        """深度拷貝字典dict中的所有屬性"""
        self.__dict__ = deepcopy(dict)

    def getAttributes(self):
        """獲取屬性字典"""
        return self.__dict__


class Caretaker:
    """備忘錄管理類"""

    def __init__(self):
        self._mementos = {}

    def addMemento(self, name, memento):
        self._mementos[name] = memento

    def getMemento(self, name):
        return self._mementos[name]

class Originator:
    """備份發起人"""

    def createMemento(self):
        memento = Memento()
        memento.setAttributes(self.__dict__)
        return memento

    def restoreFromMemento(self, memento):
        self.__dict__.update(memento.getAttributes())


# 基於框架的實現
#==============================

# Test
#=======================================================================================================================

def testEngineer():
    tony = Engineer("Tony")
    tony.addWorkItem("解決線上部分用戶因暱稱太長而無法顯示全的問題")
    tony.addWorkItem("完成PDF的解析")
    tony.addWorkItem("在閱讀器中顯示PDF第一頁的內容")
    tony.showWorkItem()
    caretaker = TodoListCaretaker()
    caretaker.setTodoList(tony.writeTodoList())

    print()
    tony.forget()
    tony.showWorkItem()

    print()
    tony.retrospect(caretaker.getTodoList())
    tony.showWorkItem()

# testEngineer()