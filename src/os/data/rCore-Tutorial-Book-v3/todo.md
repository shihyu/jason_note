# 對於一些概念等，要有一些比較具體的對應
# 對於如何一步一步實現，需要有階段性的實驗結果

## ch0
### 2os-interface
- 缺少對明確rcore-tutorial 系統調用的概述

### 3os-hw-abstract.html
- 各種抽象能否有些具體的代碼對應？

### 4os-features
- 特徵能用代碼運行來展現嗎？

### 5setup-devel-env
- 想把k210相關的挪到附錄中

最後有個Q&A比較好


## ch1

三葉蟲需要的海洋（硬件）和食物（rustsbi），通過請求sbi call 獲得輸出能力

- 介紹應用，以及圍繞應用的環境

- 解釋 sbi 新的參數約定

## ch2
- 引言 對應用程序的進一步講解
- 特權級在這一章不是必須的

## ch3-ch9
- 引言 對應用程序的進一步講解

## ch4
- 頁面置換算法的實踐體現

## ch5 
- 調度算法的實踐體現

## ch6
-  從應用角度出發，基於ram來講解，並逐步擴展，比較方便

## ch7
- 需要循序漸進

## ch8
- 銀行家算法的實現
- 死鎖檢測算法的實現

## ch9 
- 內核允許中斷
- 輪詢，中斷，DMA方式的實際展示
- 各種驅動的比較詳細的分析

## convert
make epub //build epub book
calibre // convert epub to docx
