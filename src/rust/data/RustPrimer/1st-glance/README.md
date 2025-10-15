Rust 是一門系統級編程語言，被設計為保證內存和線程安全，並防止段錯誤。作為系統級編程語言，它的基本理念是 “零開銷抽象”。理論上來說，它的速度與 C / C++ 同級。

Rust 可以被歸為通用的、多範式、編譯型的編程語言，類似 C 或者 C++。與這兩門編程語言不同的是，Rust 是線程安全的！

Rust 編程語言的目標是，創建一個高度安全和併發的軟件系統。它強調安全性、併發和內存控制。儘管 Rust 借用了 C 和 C++ 的語法，它不允許空指針和懸掛指針，二者是 C 和 C++ 中系統崩潰、內存洩露和不安全代碼的根源。

Rust 中有諸如 if else 和循環語句 for 和 while 的通用控制結構。和 C 和 C++ 風格的編程語言一樣，代碼段放在花括號中。

Rust 使用實現（implementation）、特徵（trait）和結構化類型（structured type）而不是類（class）。這點，與基於繼承的OO語言 C++, Java 有相當大的差異。而跟 Ocaml, Haskell 這類函數式語言更加接近。

Rust 做到了內存安全而無需 .NET 和 Java 編程語言中實現自動垃圾收集器的開銷，這是通過所有權/借用機制、生命週期、以及類型系統來達到的。

下面是一個代碼片段的例子，經典的 Hello World 應用：

``` rust
fn main() {
  println!("hello, world");
}
```

影響了 Rust 的流行的編程語言包括 C, C++, C#, Erlang, Haskell, OCaml, Ruby, Scheme 和 Swift 等等。Rust 也影響了 C# 7, Elm, Idris, Swift。

Rust 提供了安裝程序，你只需要從官網下載並在相應的操作系統上運行安裝程序。安裝程序支持 Windows、Mac 和 Linux（通過腳本）上的32位和64位 CPU 體系架構，適用 Apache License 2.0 或者 MIT Licenses。

Rust 運行在以下操作系統上：Linux, OS X, Windows, FreeBSD, Android, iOS。

簡單提一下 Rust 的歷史。Rust 最早是 Mozilla 僱員 Graydon Hoare 的一個個人項目，從 2009 年開始，得到了 Mozilla 研究院的支助，2010 年項目對外公佈。2010 ～2011 年間實現的自舉。從此以後，Rust 經歷了巨大的設計變化和反覆（歷程極其艱辛），終於在 2015 年 5 月 15日發佈了 1.0 版。在這個研發過程中，Rust 建立了一個強大活躍的社區，形成了一整套完善穩定的項目貢獻機制（這是真正的可怕之處）。Rust 現在由 Rust 項目開發者社區（https://github.com/rust-lang/rust ）維護。

自 15 年 5 月 1.0 發佈以來，湧現了大量優秀的項目（可以 github 上搜索 Rust 查找），大公司也逐漸積極參與 Rust 的應用開發，以及回饋開源社區。

本書（RustPrimer）旨在為中文 Rustaceans 初學者提供一個正確、最新、易懂的中文教程。本書會一直完善跟進，永不停歇。

本書是整個 Rust 中文社區共同努力的結果。其中，參與本書書寫及校訂的 Rustacean 有（排名不分先後）：

- [daogangtang（Mike貓）](https://github.com/daogangtang)
- [wayslog（貓貓反抗團團長）](https://github.com/wayslog)
- [marvin-min](https://github.com/marvin-min)
- [tiansiyuan](https://github.com/tiansiyuan)
- [marvinguo](https://github.com/marvinguo)
- ee0703
- fuyingfuying
- qdao
- JohnSmithX
- [stormgbs (AX) ](https://github.com/stormgbs)
- tennix
- anzhihun
- zonyitoo（Elton, e貓）
- 42
- [Naupio（N貓）](https://github.com/Naupio)
- F001（失落的神喵）
- wangyu190810
- domty
- [MarisaKirisame（帥氣可愛魔理沙）](https://github.com/MarisaKirisame)
- [Liqueur Librazy](https://github.com/Librazy)
- [Knight42](https://github.com/knight42)
- [Ryan Kung](https://github.com/ryankung)
- lambdaplus
- doomsplayer
- lucklove
- veekxt
- lk-chen
- RyanKung
- arrowrowe
- marvin-min
- ghKelo
- wy193777
- domty
- xusss
- wangyu190810
- nextzhou
- zhongke
- [ryuki](https://github.com/3442853561)
- codeworm96
- anzhihun
- lidashuang
- sceext2
- loggerhead
- twq0076262
- passchaos
- yyrust
- markgeek
- ts25504
- overvenus
- Akagi201
- theJian
- jqs7
- ahjdzx
- chareice
- chenshaobo
- marvinguo
- izgzhen
- ziqin
- peng1999

等。在此，向他們的辛苦工作和無私奉獻表示尊敬和感謝！

祝用 Rust 編程愉快！
