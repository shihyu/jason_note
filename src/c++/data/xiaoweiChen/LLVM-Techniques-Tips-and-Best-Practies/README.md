# LLVM Techniques, Tips, and Best Practices 

Clang and Middle-End Libraries

Design powerful and reliable compilers using the latest libraries and tools from LLVM

(*Clang和中端庫 - 使用最新的LLVM庫和工具設計強大且可靠的編譯器*)

* 作者：[Min-Yih Hsu 許民易](https://github.com/mshockwave)

* 譯者：陳曉偉

* 首次發佈時間：2021年4月22日([來源](https://www.amazon.com/Techniques-Practices-Clang-Middle-End-Libraries/dp/1838824952))

> 翻譯是譯者用自己的思想，換一種語言，對原作者想法的重新闡釋。鑑於我的學識所限，誤解和錯譯在所難免。如果你能買到本書的原版，且有能力閱讀英文，請直接去讀原文。因為與之相較，我的譯文可能根本不值得一讀。
>
> <p align="right"> — 雲風，程序員修煉之道第2版譯者</p>

## 本書概述

編譯器將高級編程語言轉換為低層機器可執行的代碼，所以每個程序員或工程師，在職業生涯的某個時刻，都會與編譯器一起優化應用程序。LLVM為開發者提供了基礎設施、庫和(開發人員構建自己的)編譯器所需的工具。使用LLVM的工具集，可以有效地為不同的後端生成代碼，並進行優化。

本書將探索LLVM編譯器的基礎結構，並介紹如何來解決問題。我們從查看LLVM重要組件的結構和設計理念開始，逐步使用Clang庫來構建分析高級源代碼的工具。隨著瞭解的深入，本書將向介紹如何處理LLVM IR——用以轉換和優化源碼。瞭解了這些，就將能夠利用LLVM和Clang創建編程語言工具，包括編譯器、解釋器、IDE和源代碼分析程序。

本書的最後，可以使用LLVM框架創建強大的工具技能，以應對現實中的各種挑戰。

#### 關鍵特性

- (以務實的方式)探索Clang，LLVM的中端和後端
- 點亮LLVM的各個技能點，並掌握各種常見用例
- 通過示例應對實際的LLVM開發

#### 內容綱要

- 瞭解LLVM的構建系統是如何工作的，以及如何減少構建資源
- 掌握使用LLVM的LIT框架運行自定義測試的方法
- 為Clang構建不同類型的插件和擴展
- 基於Clang自定義工具鏈和編譯器標誌
- 為PassManager寫LLVM Pass
- 瞭解如何檢查和修改LLVM IR
- 瞭解如何使用LLVM的配置文件引導優化(PGO)框架
- 創建自定義(編譯器)消毒器



## 適讀人群

本書適用於所有具有LLVM工作經驗的軟件工程師，本書會提供了簡明的開發指南和參考。如果你是一名學術研究者，這本書將助你在短時間內學習有用的LLVM技能，使你能夠快速構建項目原型。編程語言愛好者也會發現這本書中的內容，在LLVM的幫助下構建一種新的編程語言也十分有趣



## 作者簡介

**Min-Yih "Min" Hsu**是加州大學歐文分校計算機科學博士研究生。他的研究集中在編譯器工程、代碼優化、高級硬件架構和系統安全。2015年起，他一直是LLVM社區的活躍成員，並貢獻了許多補丁。他還致力於通過各種途徑倡導LLVM和編譯器工程，比如寫博客和發表演講。在業餘時間，他喜歡瞭解各種不同的咖啡豆和煮咖啡的方法。

> 我要感謝所有支持過我的人，特別是家人和導師。還要感謝LLVM社區不論出身的包容和善待每一位成員。
>
> <p align="right"> —Min-Yih Hsu</p>

## 審評者介紹

**Suyog Sarda**是一名專業的軟件工程師和開源愛好者，專注於編譯器開發和編譯器工具，是LLVM開源社區的積極貢獻者。他畢業於了印度浦那工程學院，具有計算機技術學士學位。Suyog還參與了ARM和X86架構的代碼性能改進，一直是Tizen項目編譯團隊的一員，對編譯器開發的興趣在於代碼優化和向量化。之前，他寫過一本關於LLVM的書，名為《LLVM Cookbook》，由Packt出版。除了編譯器，Suyog還對Linux內核開發感興趣。他在迪拜Birla Institute of Technology的2012年IEEE Proceedings of the International Conference on Cloud Computing, Technologies, Applications, and Management上發表了一篇題為《VM pin and Page Coloring Secure Co-resident Virtualization in Multicore Systems》的技術論文。

他在浦那工程學院獲得了技術學士學位。到目前為止，他的工作主要與編譯器有關，並他對編譯器的性能方面特別感興趣。他曾致力於DSP圖像處理語言的研究，使用LLVM的模塊化特性可以根據編譯器的需求快速實現。然而，LLVM的文檔比較分散，他希望這本書可以為LLVM編譯器基礎架構提供一種綜合性的概述。



## 本書相關

* github翻譯地址：https://github.com/xiaoweiChen/LLVM-Techniques-Tips-and-Best-Practies
* 譯文的LaTeX 環境配置：https://www.cnblogs.com/1625--H/p/11524968.html 

