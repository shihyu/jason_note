<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第十二章：併發編程](#%E7%AC%AC%E5%8D%81%E4%BA%8C%E7%AB%A0%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B)
  - [12.1 基於進程的併發編程](#121-%E5%9F%BA%E4%BA%8E%E8%BF%9B%E7%A8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B)
  - [12.2 基於IO多路複用的併發編程](#122-%E5%9F%BA%E4%BA%8Eio%E5%A4%9A%E8%B7%AF%E5%A4%8D%E7%94%A8%E7%9A%84%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B)
  - [12.3 基於線程的併發編程](#123-%E5%9F%BA%E4%BA%8E%E7%BA%BF%E7%A8%8B%E7%9A%84%E5%B9%B6%E5%8F%91%E7%BC%96%E7%A8%8B)
  - [12.4 多線程程序中的共享變量](#124-%E5%A4%9A%E7%BA%BF%E7%A8%8B%E7%A8%8B%E5%BA%8F%E4%B8%AD%E7%9A%84%E5%85%B1%E4%BA%AB%E5%8F%98%E9%87%8F)
  - [12.5 用信號量同步線程](#125-%E7%94%A8%E4%BF%A1%E5%8F%B7%E9%87%8F%E5%90%8C%E6%AD%A5%E7%BA%BF%E7%A8%8B)
  - [12.6 使用線程提高並行性](#126-%E4%BD%BF%E7%94%A8%E7%BA%BF%E7%A8%8B%E6%8F%90%E9%AB%98%E5%B9%B6%E8%A1%8C%E6%80%A7)
  - [12.7 其他併發問題](#127-%E5%85%B6%E4%BB%96%E5%B9%B6%E5%8F%91%E9%97%AE%E9%A2%98)
    - [可重入性](#%E5%8F%AF%E9%87%8D%E5%85%A5%E6%80%A7)
    - [在多線程程序中使用庫函數](#%E5%9C%A8%E5%A4%9A%E7%BA%BF%E7%A8%8B%E7%A8%8B%E5%BA%8F%E4%B8%AD%E4%BD%BF%E7%94%A8%E5%BA%93%E5%87%BD%E6%95%B0)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第十二章：併發編程

前面的例子中：硬件異常處理程序、進程、Linux信號處理都是併發程序的例子。應用級併發在以下情況會很有用：
- 訪問慢速IO設備。
- 與人交互。
- 推遲工作降低延遲。
- 服務多個網絡客戶端。
- 在多核機器上進行併發計算。

現代操作系統中構造併發程序的方式：
- 進程：通過進程間通信與其他進程交互。
- IO多路複用：顯式調度自己的控制流。
- 線程。

## 12.1 基於進程的併發編程

併發編程的最簡單方式，使用`fork exec waitpid`等接口。
- 進程間共享文件表，但是不共享用戶地址空間。
- 獨立的地址空間讓進程共享狀態信息變得困難。為了共享信息，需要使用顯式的IPC機制。
- 進程往往比較慢，進程控制和IPC開銷很高。
- IPC（進程間通信）：
    - 最基本機制：比如waitpid、信號。
    - 套接字是另一個形式。
    - 還有其他形式：管道，FIFO、共享內存、信號量。

## 12.2 基於IO多路複用的併發編程

即是異步IO，在等待IO時要求內核掛起進程，在一個或者多個事件發生後才返回。

## 12.3 基於線程的併發編程

Linux下標準線程庫是pthread：
- 創建線程：`pthread_create`。
- 獲取自己的線程ID：`pthread_self`。
- 終止線程：`pthread_exit`。
- 取消線程：`pthread_cancel`。
- 等待線程終止：`pthread_join`。
- 分離線程：`pthread_detach`。

## 12.4 多線程程序中的共享變量

## 12.5 用信號量同步線程

## 12.6 使用線程提高並行性

## 12.7 其他併發問題

### 可重入性

可重入函數是線程安全函數的真子集：可重入函數不會引用任何共享數據。

### 在多線程程序中使用庫函數

可以參考文檔查看一個函數是否是線程安全的：
- 大多數Linux函數是線程安全的，小部分例外。
- Linux系統提供大多數線程不安全函數的可重入版本，這些函數以後綴`_r`結尾。比如`rand`是線程不安全的，它的可重入版本是`rand_r`。
