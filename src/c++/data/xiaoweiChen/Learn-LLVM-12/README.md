# Learn LLVM 12
A beginner's guide to learning LLVM compiler tools and core libraries with C++ 

(*使用C++學習LLVM編譯器和核心庫的初學者教程*)

* 作者：Kai Nacke

* 譯者：陳曉偉

* 原文發佈時間：2021年5月28日 (來源亞馬遜)

> 翻譯是譯者用自己的思想，換一種語言，對原作者想法的重新闡釋。鑑於我的學識所限，誤解和錯譯在所難免。如果你能買到本書的原版，且有能力閱讀英文，請直接去讀原文。因為與之相較，我的譯文可能根本不值得一讀。
>
> <p align="right"> — 雲風，程序員修煉之道第2版譯者</p>

## 本書概述

學習如何構建和使用編譯器，包括前端、流水線優化和利用LLVM核心庫的強大功能構建新的後端編譯器。

LLVM是為了彌合編譯器理論和實際開發之間的差異而出現的。它提供了模塊化的代碼庫和先進的工具，幫助開發人員輕鬆地構建編譯器。本書提供了對LLVM的介紹，幫助讀者在各種情況下構建和使用編譯器。

本書將從配置、構建和安裝LLVM庫、工具和外部項目開始。接著，向您介紹LLVM的設計，以及在每個編譯器階段(前端、優化器和後端)的實際工作方式。以實際編程語言為例，學習如何使用LLVM開發前端編譯器，並生成LLVM IR，將其交給優化流水線，並從中生成機器碼。後面的章節將展示如何擴展LLVM，以及LLVM中的指令選擇是如何工作的。在瞭解如何為LLVM開發新的後端編譯器之前，將重點討論即時編譯問題和LLVM提供的JIT編譯的支持情況。

閱讀本書後，您將獲得使用LLVM編譯器開發框架的實際經驗，並得到一些具有幫助性的實際示例和源代碼片段。

#### 關鍵特性

- 學習如何有效地使用LLVM
- 理解LLVM編譯器的高級設計，並將原則應用到自己的編譯器中
- 使用基於編譯器的工具來提高C++項目的代碼質量

#### 內容綱要

- 配置、編譯和安裝LLVM框架
- 理解LLVM源碼的結構
- 瞭解在項目中可以使用LLVM做什麼
- 探索編譯器是如何構造的，並實現一個小型編譯器
- 為通用源語言構造生成LLVM IR
- 建立優化流水線，並根據自己的需要進行調整
- 使用轉換通道和clang工具對LLVM進行擴展
- 添加新的機器指令和完整的後端編譯器



## 作者簡介

**Kai Nacke**是一名專業IT架構師，目前居住在加拿大多倫多。畢業於德國多特蒙德技術大學的計算機科學專業。他關於通用哈希函數的畢業論文，被評為最佳論文。

他在IT行業工作超過20年，在業務和企業應用程序的開發和架構方面有豐富的經驗。他在研發一個基於LLVM/Clang的編譯器。

幾年來，他一直是LDC(基於LLVM的D語言編譯器)的維護者。在Packt出版過《D Web Development》一書，他也曾在自由和開源軟件開發者歐洲會議(FOSDEM)的LLVM開發者室做過演講。



## 審評者介紹

**Suyog Sarda**是一名專業的軟件工程師和開源愛好者，專注於編譯器開發和編譯器工具，是LLVM開源社區的積極貢獻者。他畢業於了印度浦那工程學院，具有計算機技術學士學位。Suyog還參與了ARM和X86架構的代碼性能改進，一直是Tizen項目編譯團隊的一員，對編譯器開發的興趣在於代碼優化和向量化。之前，他寫過一本關於LLVM的書，名為《LLVM Cookbook》，由Packt出版。除了編譯器，Suyog還對Linux內核開發感興趣。他在迪拜Birla Institute of Technology的2012年IEEE Proceedings of the International Conference on Cloud Computing, Technologies, Applications, and Management上發表了一篇題為《VM pin and Page Coloring Secure Co-resident Virtualization in Multicore Systems》的技術論文。



## 本書相關

* github翻譯地址：https://github.com/xiaoweiChen/Learn-LLVM-12
* 本書代碼：https://github.com/PacktPublishing/Learn-LLVM-12
* 譯文的LaTeX 環境配置：https://www.cnblogs.com/1625--H/p/11524968.html 

