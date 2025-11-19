# Modern CMake for C++  

*Discover a better approach to building, testing, and packaging your software*

*(構建、測試和打包軟件)*

<a href="https://www.packtpub.com/product/modern-cmake-for-c/9781801070058"><img src="https://static.packt-cdn.com/products/9781801070058/cover/smaller" height="256px" align="right"></a>

* 作者：Rafał Świdziński
* 譯者：陳曉偉
* 首次發佈時間：2022年2月28日([來源](https://www.amazon.com/Modern-CMake-Discover-approach-packaging/dp/1801070059))

> 翻譯是譯者用自己的思想，換一種語言，對原作者想法的重新闡釋。鑑於我的學識所限，誤解和錯譯在所難免。如果你能買到本書的原版，且有能力閱讀英文，請直接去讀原文。因為與之相較，我的譯文可能根本不值得一讀。
>
> <p align="right"> — 雲風，程序員修煉之道第2版譯者</p>

PDF可在本庫的[Release頁面](https://github.com/xiaoweiChen/Modern-CMake-for-Cpp/releases)獲取。

## 本書概述

創建一流的軟件非常困難，開發人員很難確定哪些建議是最新的，哪些方法已經可以用更簡單、更好的實踐所取代。與此同時，大多數在線資源提供的解釋有限，也缺乏相應的上下文。

本書提供了一種更簡單、更全面的體驗，介紹瞭如何構建C++解決方案。Modern CMake for C++是一個端到端的任務自動化指南，包括構建、測試和打包。不僅可以瞭解如何在項目中使用CMake語言，還可以瞭解如何使它們可維護，優雅和乾淨。本書還關注源目錄、構建目標和包的結構。隨著瞭解的深入，將學習如何編譯和鏈接可執行文件和庫，這些過程如何工作，以及如何優化CMake中的構建得最佳結果。還將瞭解如何在項目中使用外部依賴項——第三方庫、測試框架、程序分析工具和文檔生成器。最後，導出內部和外部目標，以及安裝和打包。

讀完這本書，就能夠自信地使用CMake了。

#### 關鍵特性

- 理解並自動化CMake編譯和鏈接

- 管理內部和外部依賴關係
- 添加質量檢查和測試作為構建步驟

#### 將會學到

- 瞭解構建C++代碼的最佳實踐
- 通過使用來獲得CMake語言的實踐知識
- 在測試、靜態和動態分析的幫助下，使用前沿工具來保證代碼質量
- 瞭解如何使用CMake管理、發現、下載和鏈接依賴關係
- 構建可長期重用和維護的解決方案
- 瞭解如何優化構建構件和構建過程本身



## 適讀人群

這本書是為具有C/ C++編程知識的工程師和軟件開發人員所著，從而可以學習CMake，以瞭解自動化構建小型和大型軟件的解決方案。若剛剛開始使用CMake，並長期使用GNU Make，或者只是想複習一下最新的最佳實踐，那麼本書非常適合您。

## 作者簡介

**Rafał Świdziński**在Google公司擔任工程師，具有超過10年專業經驗的全棧開發人員，瞭解大量的編程語言和技術，一直在自己的公司和包括Cisco Meraki、Amazon和Ericsson在內的公司開發軟件。他來自波蘭的羅茲(Łódź)，現在生活在英國倫敦，在那裡經營一個YouTube頻道“Smok”，討論與軟件開發相關的話題。他很喜歡處理技術問題，包括該領域的挑戰。在工作中，他了解各種技術概念，並揭開了軟件工程師角色背後的藝術和科學的神秘面紗。他的主要關注代碼質量和編程技巧。

> 感謝我的家人:我的父母Bożena和Bogdan，我的姐妹Ewelina和Justyna，以及我的妻子Katarzyna，感謝他們一直以來的支持和建議。
>
> <p align="right"> — Rafał Świdziński</p>

## 審評者介紹

**Sergio Guidi Tabosa Pessoa** 是一名軟件工程師，在軟件開發和維護方面有超過30年的經驗，從複雜的企業軟件項目到現代移動應用。早期主要與Microsoft打交道，但很快就喜歡上了UNIX和Linux操作系統的強大功能。儘管他多年來使用過許多語言，但C和C++仍因其強大的功能和速度而成為他最喜歡的語言。

他擁有計算機科學學士學位和IT管理工商管理碩士學位，總是渴望學習新技術，破解代碼，從錯誤中學習。目前和妻子，兩隻約克郡犬和兩隻鸚鵡生活在巴西。

> 首先，我要感謝參與這個項目的所有人，包括精心製作瞭如此偉大作品的作者，以及給我這個機會的Packt  Publishing。我也要感謝我美麗的妻子Lucia，以及Touché和Lion，感謝他們的耐心和給我所需的時間來幫助

**Eric Noulard**擁有法國ENSEEIHT的工程學學位和法國UVSQ的計算機科學博士學位。20年來，他一直在用各種語言編寫和編譯源代碼。自2006年以來一直是CMake的用戶，多年來一直是該項目的積極貢獻者。職業生涯中，Eric曾為私人公司和政府機構工作。現在受僱於Antidot，這是一家軟件供應商，負責開發和營銷高端信息檢索技術和解決方案。

**Mohammed Alqumairi**是Cisco Meraki的軟件工程師，使用各種語言和框架開發關鍵和性能後端服務方面有經驗，尤其關注現代C++、CMake和Poco庫。Mohammed以優異的成績畢業於倫敦城市大學，獲得計算機科學學士學位。

## 本書相關

* github地址：https://github.com/xiaoweiChen/Modern-CMake-for-Cpp
* 譯文的LaTeX 環境配置：https://www.cnblogs.com/1625--H/p/11524968.html 
  * 禁用拼寫檢查：https://blog.csdn.net/weixin_39278265/article/details/87931348

* vscode中配置latex：https://blog.csdn.net/Ruins_LEE/article/details/123555016
* 原書示例：https://github.com/PacktPublishing/Modern-CMake-for-Cpp

