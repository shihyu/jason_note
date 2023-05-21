
Heterogeneous Computing with OpenCL 2.0
=========================
*Third Edition*
-------------------------
- 作者：David Kaeli, Perhaad Mistry, Dana Schaa, Dong Ping Zhang
- 譯者：陳曉偉

## 本書概述

作為對《Heterogeneour Computing with OpenCL 2.0 (Thrid Edition)》英文版的中文翻譯。

本書將介紹在複雜環境下的OpenCL和並行編程。這裡的複雜環境包含多種設備架構，比如：多芯CPU，GPU，以及完全集成的加速處理單元(APU)。在本修訂版中將包含OpenCL 2.0最新的改進：
- 共享虛擬內存(*Shared virtual memory*)可增強編程的靈活性，從而能大幅度減少在數據轉換上所消耗的資源和精力 
- 動態並行(*Dynamic parallelism*)將減少處理器上的負載，並避免瓶頸出現
- 對圖像的支持有很大改善，並且集成OpenGL

為了能在不同的平臺上進行工作，OpenCL將有助你充分發揮出異構平臺的能力。本書的作者們都是異構計算和OpenCL社區的佼佼者，本書涉及到的內容有：內存空間、優化技能、相關擴展、調試與分析。書中還會涉及多個實際的案例，來展示高性能的算法、異構系統如何分配工作，以及嵌入式領域特殊的語言。當然，也會讓讀者使用OpenCL來實現一些基本算法的並行版本：
- 使用最新OpenCL 2.0標準的特性，包括內存處理、動態並行和圖像特性
- 對實際的程序進行測試和調試，從而對抽象的模型概念進行理解，並解釋使用OpenCL進行並行編程的準則及策略
- 本書的案例包含：圖像分析、Web插件、粒子模擬、視頻編輯、性能優化，等等

## 本書作者

### David Kaeli

David Kaeli在羅格斯大學(Rutgers University)獲得電氣工程學士和博士學位，在雪城大學(Syracuse University)獲得計算機工程碩士學位，並管理東北大學計算機體系研究室(NUCAR)。1993年Kaeli加入東北大學，他之前在IBM任職12年，任職的最後7年在T.J. Watson研究中心(位於紐約，約克敦海茨)度過。現在，在東北大學工程學院(本科)(位於美國東北部，馬薩諸塞州，州府波士頓)任職副院長，為ECE(電子和計算機工程專業，Electrical and Computer Engineering)系的系主任。

Kaeli博士合著超過200個學術出版物，其研究領域跨度也非常大，從微體系結構到後端編譯器和軟件工程。他主導了很多GPU計算方面的研究項目，並且現在是IEEE技術委員會，計算機體系結構方面的主席。他也是IEEE院士，以及ACM(國際計算機學會，Association for Computing Machinery)成員。

### Perhaad Mistry

Perhaad Mistry作為AMD公司工具組開發成員，任職於在位於波士頓設計中心，主要研究異構結構下使用的調試和性能分析工具，現居波士頓。他目前主要研究的是“共享內存及離散式GPU平臺”(將要到來的平臺)上的調試工具的研究。自2007年CUDA0.8發佈後，Perhaad就開始研究GPU的架構和並行計算。他很喜歡使用GPGPU來實現醫學成像算法，以及設計外科模擬器的感知數據結構。Perhaad目前在為下一代GPU平臺研究調試工具和性能分析工具。

David Kaeli博士曾在學校建議Perhaad加入NUCAR。雖然，已經離開東北大學已經7年(在東北大學電子和計算機工程專業取得博士學位)，但是Perhaad仍然是NUCAR的一員，並且在並行相關的性能分析項目上給出中肯的建議。其在孟買大學(印度3所歷史最悠久、規模最大的綜合性大學之一)獲得電氣工程學士學位，並在東北大學獲得計算機工程碩士學位。

### Dana Schaa

Dana Schaa在加州州立理工大學(Cal Poly，位於神路易斯奧比斯波，舊金山和洛杉磯的中間位置)獲得計算機工程學士學位，並在東北大學獲得電子和計算機專業碩士和博士學位。他在AMD公司為GPU架構建模，並且對GPU的內存系統、微架構、性能分析和通用計算十分感興趣，也在這些方面表現的相當專業。他開發了一些基於OpenCL的醫學影像應用，從實時三維超聲到異構CT(電子計算機斷層掃描，Computed Tomography)圖像重構。2010年，Dana與其女友Jenny完婚，現在他們和他們可愛的喵都住在聖何塞。

### 張東萍(Dong Ping Zhang)

東萍(音譯)在英國帝國學院(Imperial College London)獲得計算機博士學位。她博士期間的研究方向是“時域和空域上的大型多模態生物醫學分析”。現任職與AMD公司，為“百億億次級計算研究組”工作。其研究方向和AMD公司“異構系統架構組”有著很密切的合作。

加入AMD公司之前，她在帝國學院計算機系做博士後研究。2006年，在先進計算方面獲得理學碩士學位。2010年，在計算機科學方面獲得博士學位。這兩個學位均由Daniel Rueckert教授授予(Daniel Rueckert教授曾在醫學圖像分析領域獲得“2010年度世界最佳導師”稱號)。2009年，她還曾在鹿特丹Erasmus醫學中心作為生物醫學成像組成員，短暫的工作過一段時間。

## 本書相關

- github 翻譯地址：https://github.com/xiaoweiChen/Heterogeneous-Computing-with-OpenCL-2.0
