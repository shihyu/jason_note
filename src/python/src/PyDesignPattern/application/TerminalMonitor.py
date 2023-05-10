#!/usr/bin/python
# Authoer: Spencer.Luo
# Date: 5/20/2018

# 引入升級版備忘錄模式關鍵類
from pattern.Memento import Originator, Caretaker, Memento
import logging

class TerminalCmd(Originator):
    """終端命令"""

    def __init__(self, text):
        self.__cmdName = ""
        self.__cmdArgs = []
        self.parseCmd(text)

    def parseCmd(self, text):
        """從字符串中解析命令"""
        subStrs = self.getArgumentsFromString(text, " ")
        # 獲取第一個字段作為命令名稱
        if(len(subStrs) > 0):
            self.__cmdName = subStrs[0]

        # 獲取第一個字段之後的所有字符作為命令的參數
        if (len(subStrs) > 1):
            self.__cmdArgs = subStrs[1:]

    def getArgumentsFromString(self, str, splitFlag):
        """通過splitFlag進行分割，獲得參數數組"""

        if (splitFlag == ""):
            logging.warning("splitFlag 為空!")
            return ""

        data = str.split(splitFlag)
        result = []
        for item in data:
            item.strip()
            if (item != ""):
                result.append(item)

        return result;

    def showCmd(self):
        print(self.__cmdName, self.__cmdArgs)

class TerminalCaretaker(Caretaker):
    """終端命令的備忘錄管理類"""

    def showHistoryCmds(self):
        """顯示歷史命令"""
        for key, obj in self._mementos.items():
            name = ""
            value = []
            if(obj._TerminalCmd__cmdName):
                name = obj._TerminalCmd__cmdName
            if(obj._TerminalCmd__cmdArgs):
                value = obj._TerminalCmd__cmdArgs
            print("第%s條命令: %s %s" % (key, name, value) )


def testTerminal():
    cmdIdx = 0
    caretaker = TerminalCaretaker()
    curCmd = TerminalCmd("")
    while (True):
        strCmd = input("請輸入指令：");
        strCmd = strCmd.lower()
        if (strCmd.startswith("q")):
            exit(0)
        elif(strCmd.startswith("h")):
            caretaker.showHistoryCmds()
        # 通過"!"符號表示獲取歷史的某個指令
        elif(strCmd.startswith("!")):
            idx = int(strCmd[1:])
            curCmd.restoreFromMemento(caretaker.getMemento(idx))
            curCmd.showCmd()
        else:
            curCmd = TerminalCmd(strCmd)
            curCmd.showCmd()
            caretaker.addMemento(cmdIdx, curCmd.createMemento())
            cmdIdx +=1


testTerminal()