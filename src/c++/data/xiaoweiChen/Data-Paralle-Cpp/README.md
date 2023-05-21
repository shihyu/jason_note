# Data Parallel C++
*Mastering DPC++ for Programming of Heterogeneous Systems using C++ and SYCL（掌握DPC++：使用C++和SYCL語言進行異構編程）*

* 作者：

  James Reinders 

  Ben Ashbaugh

  James Brodman

  Michael Kinsner

  John Pennycook

  Xinmin Tian

* 譯者：陳曉偉

* 原文發佈時間：2020年09月02日

> 翻譯是譯者用自己的思想，換一種語言，對原作者想法的重新闡釋。鑑於我的學識所限，誤解和錯譯在所難免。如果你能買到本書的原版，且有能力閱讀英文，請直接去讀原文。因為與之相較，我的譯文可能根本不值得一讀。
>
> <p align="right"> — 雲風，程序員修煉之道第2版譯者</p>

## 本書概述

本書是關於使用C++編寫數據並行程序的。如果你是並行編程的新手，也沒關係。如果從未聽說過SYCL或DPC++編譯器，也沒有關係。

SYCL是一個行業驅動的Khronos標準，在異構系統為C++中添加原生的數據並行性。DPC++是一個開源編譯器項目，它基於SYCL、編譯器擴展和異構支持組成，其中包括GPU、CPU和FPGA支持。本書中的所有例子都是用DPC++編譯器編譯的。

如果你是一個不精通C++的C程序員，不用太擔心。本書的幾位作者會告訴你，他們是通過閱讀使用C++的書籍來學習C++的，就像這本書一樣。只要有一點耐心，這本書對於想要編寫現代C++程序的C程序員來說應該是很容易的。

本書項目始於2019年，對於完全支持C++和數據並行的需要大量的擴展，超出當時的SYCL 1.2.1標準。DPC++編譯器需要支持這些擴展，包括對統一共享內存(USM)的支持、通過SYCL完成三級層次結構的子組、匿名lambdas和許多編程簡化。

本書出版的時候(2020年末)，會有一個臨時的SYCL 2020規範可供公眾評論。臨時規範包括對USM、子組、匿名lambdas的支持，以及對編碼的簡化(類似於C++ 17 CTAD)。可以通過本書中SYCL的擴展，以大致瞭解SYCL將來的發展方向，這些擴展都會在DPC++編譯器項目中實現。我們希望與本書的內容相比，SYCL的變化不會太大，但隨著社區的發展，SYCL將會有一些變化。更新信息的重要資源包括本書GitHub和勘誤表，可以從本書的網頁(www.apress.com/9781484255735)找到，以及oneAPI DPC++參考(tinyurl.com/dpcppref)。

SYCL和DPC++的發展仍在繼續。在學習瞭如何使用DPC++為使用SYCL的異構系統創建程序之後，會在之後討論對未來的展望。

希望我們的書能夠支持和幫助SYCL社區的發展，並幫助推廣C++中的數據並行編程。

## 作者簡介

**James Reinders**是並行計算領域有30多年經驗的專家，參與編纂了十餘本與並行編程相關的技術書籍，以及為世界上最快的兩臺計算機(500強中排名第一)以及許多其他超級計算機和軟件開發工具做出了重要貢獻。2016年中期結束在Intel的任期(已經在Intel工作了10,001天(超過27年)），不過還繼續在並行計算(高性能計算和人工智能)相關的領域進行寫作、教學和編程。

**Ben Ashbaugh**是Intel公司的軟件架構師，他工作了20多年，為Intel圖形產品開發軟件驅動程序。在過去的10年裡，Ben專注於並行編程模型，用於圖形處理器上的通用計算，包括SYCL和DPC++。Ben活躍於Khronos SYCL、OpenCL和SPIR工作組，幫助定義並行編程的行業標準，他編寫了許多擴展來展示Intel GPU獨特的魅力。

**James Brodman**是Intel公司的軟件工程師，專注於並行編程的運行時和編譯器開發，並且是DPC++的架構師之一。他擁有伊利諾伊大學厄巴納-香檳分校的計算機博士學位。

**Michael Kinsner**是Intel公司的首席工程師，為各種架構開發並行編程語言和模型，也是DPC++的架構師之一。他對空間編程模型和編譯器做出了重要的貢獻，是Khronos組織中的Intel代表，他致力於制定SYCL和OpenCL並行編程行業標準。Mike擁有麥克馬斯特大學(McMaster University)的計算機工程博士學位，並且熱衷於編寫跨架構的編程模型(同時能夠保證性能)。

**John Pennycook**是Intel公司的一名HPC應用工程師，專注於讓開發人員充分利用現代處理器中的並行性。他在一系列科學領域的應用程序優化和並行方面有豐富的經驗，此前曾擔任Intel極端性能用戶組(IXPUG)指導委員會的代表。John擁有華威大學計算機科學博士學位。他的研究點很多，主要在於跨不同硬件架構實現應用“性能可移植性”的能力。

**Xinmin Tian**是Intel公司高級首席工程師和編譯架構師，在OpenMP架構審查委員會(ARB)擔任Intel代表。他負責為Intel架構驅動對OpenMP進行裝載、向量化和並行化編譯器技術。他目前的重點是基於llvm的OpenMP裝載，使用oneAPI工具包的DPC++編譯器對CPU和Xe加速器進行優化，以及優化HPC/AI應用程序性能。他擁有計算機科學博士學位，擁有27項美國專利，發表了60多篇技術論文，被1200多次引用，並在其專業領域與他人合著了兩本書。

## 本書相關

* github翻譯地址：https://github.com/xiaoweiChen/Data-Paralle-Cpp
* 英文原版PDF：https://www.apress.com/gp/book/9781484255735
* 相關教程：https://github.com/jeffhammond/dpcpp-tutorial
* Latex環境搭建：https://www.cnblogs.com/1625--H/p/11524968.html
