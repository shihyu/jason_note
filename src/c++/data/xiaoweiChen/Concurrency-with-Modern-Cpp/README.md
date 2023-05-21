# Concurrency with Modern C++

* 作者：Rainer Grimm
* 譯者：陳曉偉
* 原文發佈時間：2019年03月19日

> 翻譯是譯者用自己的思想，換一種語言，對原作者想法的重新闡釋。鑑於我的學識所限，誤解和錯譯在所難免。如果你能買到本書的原版，且有能力閱讀英文，請直接去讀原文。因為與之相較，我的譯文可能根本不值得一讀。
>
> <p align="right"> — 雲風，程序員修煉之道第2版譯者</p>

## 本書概述

每個專業的C++開發者，都應該知曉的併發性。

本書是一場關於C++併發的旅程。

* C++11和C++14創建了併發和並行的基礎件。

* C++17中，將標準模板庫(STL)的大部分算法並行化。這意味著大多數基於STL的算法可以串行、並行或向量化執行。

* C++的併發之旅並沒有停止。C++20/23中還有增強版future、協程([coroutines](https://en.cppreference.com/w/cpp/language/coroutines))、事件性內存([transactional_memory](https://en.cppreference.com/w/cpp/language/transactional_memory))等等。

本書解釋了C++中的併發性，並提供了許多代碼示例。因此，可以將理論與實踐相結合。

因為這本書與併發相關，所以我展示了很多容易出錯的地方，並展示避免或解決它們的方案。

## 書與作者

這本書使用英語完成。在寫書之前，我在我的英文博客www.ModernesCpp.com發佈了要寫這本書的消息，並得到了很多人的回覆。有大概有50多個人要幫我校對。特別感謝我的閨女Juliette，對本書的佈局進行昇華；還有我的兒子，你是本書的第一個審閱者哦。當然，還有很多很多人 : NikosAthanasiou, RobertBadea, JoeDas, Jonas Devlieghere, Randy Hormann, Lasse Natvig, Erik Newton, Ian Reeve, Bart Vandewoestyne, Dafydd Walters, Andrzej Warzynski, 以及Enrico Zschemisch。

我已經做了20多年的軟件架構師、團隊帶頭人和講師。在業餘時間，我喜歡瞭解關於C++、Python和Haskell的信息。2016年時，我決定為自己工作。我會組織關於C++和Python的研討會。

在Oberstdorf時，我換了一個新的髖關節(義肢)。本書的前半部分是在診所期間所寫，這段時間充滿挑戰，對我寫書也有很大的幫助。

## 本書相關

* github翻譯地址：https://github.com/xiaoweiChen/Concurrency-with-Modern-Cpp
* 英文原版PDF：https://ru.b-ok2.org/book/5247958/3b69d3