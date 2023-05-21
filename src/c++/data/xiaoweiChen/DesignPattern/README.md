# Design Pattern
設計模式

## 簡介

參考書籍 《圖解設計模式》，實現各種設計模式

使用C++11實現

## Build status

| [Linux][lin-link] | [Windows][win-link] | [Coveralls][cov-link] |
| :---------------: | :-----------------: | :-------------------: |
| ![lin-badge]      | ![win-badge]        | ![cov-badge]          |

[lin-badge]: https://travis-ci.org/jaredtao/DesignPattern.svg?branch=master "Travis build status"
[lin-link]: https://travis-ci.org/jaredtao/DesignPattern "Travis build status"
[win-badge]: https://ci.appveyor.com/api/projects/status/cckdwxaagrh2ncvo?svg=true "AppVeyor build status"
[win-link]: https://ci.appveyor.com/project/jiawentao/designpattern "AppVeyor build status"
[cov-badge]: https://coveralls.io/repos/github/wentaojia2014/DesignPattern/badge.svg?branch=master "Coveralls coverage"
[cov-link]: https://coveralls.io/github/wentaojia2014/DesignPattern?branch=master "Coveralls coverage"

## License
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jaredtao/TaoJson/blob/master/LICENSE)

## 目錄

|編號| 類型   | 模式         | 說明                                                                                                |
|:----:| :----: | :----------: | :-------------------------------------------------------------------------------------------------: |
| 1 | 創建型 | 工廠方法模式 | [工廠方法模式](code/Create/FactoryMethod/README.md)                                                 |
| 2 | 創建型 | 抽象工廠模式 | [抽象工廠模式](code/Create/AbstractFactory/README.md)                                               |
| 3 | 創建型 | 構建模式     | [構建模式](code/Create/Builder/README.md)                                                           |
| 4 | 創建型 | 單例模式     | [單例模式](code/Create/Singleton/README.md)                                                         |
| 5 | 創建型 | 原型模式     | [原型模式](code/Create/Prototype/README.md)                                                         |
| 6 | 結構型 | 複合模式     | [複合模式](code/Struct/Composite/README.md)                                                         |
| 7 | 結構型 | 適配器模式   | [類適配器模式](code/Struct/Adapter_01/README.md) [對象適配器模式](code/Struct/Adapter_02/README.md) |
| 8 | 結構型 | 裝飾模式     | [裝飾模式](code/Struct/Decorator/README.md)                                                         |
| 9 | 結構型 | 窗口模式     | [窗口模式](code/Struct/Facade/README.md)                                                            |
| 10 | 結構型 | 輕量模式     | [輕量模式](code/Struct/FlyWeight/README.md)                                                         |
| 11 | 結構型 | 代理模式     | [代理模式](code/Struct/Proxy/README.md)                                                             |
| 12 | 結構型 | 橋接模式     | [橋接模式](code/Struct/Bridge/README.md)                                                            |
| 13 | 行為型 | 迭代器模式   | [迭代器模式](code/Behavior/Iterator/README.md)                                                      |
| 14 | 行為型 | 模板方法模式 | [模板方法模式](code/Behavior/TemplateMethod/README.md)                                              |
| 15 | 行為型 | 策略模式     | [策略模式](code/Behavior/Strategy/README.md)                                                        |
| 16 | 行為型 | 訪問者模式   | [訪問者模式](code/Behavior/Visitor/README.md)                                                       |
| 17 | 行為型 | 責任鏈模式   | [責任鏈模式](code/Behavior/ResponsibilityChain/README.md)                                           |
| 18 | 行為型 | 仲裁者模式   | [仲裁者模式](code/Behavior/Mediator/README.md)                                                      |
| 19 | 行為型 | 觀察者模式   | [觀察者模式](code/Behavior/Observer/README.md)                                                      |
| 20 | 行為型 | 備忘錄模式   | [備忘錄模式](code/Behavior/Memento/README.md)                                                       |
| 21 | 行為型 | 狀態模式     | [狀態模式](code/Behavior/State/README.md)                                                           |
| 22 | 行為型 | 命令模式     | [命令模式](code/Behavior/Command/README.md)                                                         |
| 23| 行為型 | 解釋器模式   | [解釋器模式](code/Behavior/Interpreter/README.md)                                                   |
## 總結

### 創建型模式
創建型模式對類的實例化過程進行抽象，將軟件中對象的創建和使用分離。
為了使軟件的結構更加清晰，外界對於這些對象只需要知道共同的接口，而不清楚其內部實現細節，使整個系統的設計更加符合單一職責原則。

創建型模式在創建什麼（what） 、由誰創建（who）、何時創建（when）等方面都為軟件設計者提供了儘可能大的靈活性，隱藏了類的實例創建細節，通過隱藏對象
如何被創建和組合在一起，達到整個系統獨立的目的

### 結構型模式

描述如何將類和對象結合在一起形成更大的結構，就像搭積木，通過簡單積木的組合形成結構複雜、功能強大的結構
分為 類結構型模式 和 對象結構型模式：
* 類結構型模式 

 關心類的組合，由多個類可以組合成一個更大的
系統，在類結構型模式中一般只存在繼承關係和實現關係

* 對象結構型模式

 關心類與對象的組合，通過關聯關係使得在一 個類中定義另一個類的實例對象，然後通過該對象調用其方法。 根據“合成複用原則”，在系統中儘量使用關聯關係來替代繼 承關係，因此大部分結構型模式都是對象結構型模式。
### 行為型模式
對不同的對象之間劃分責任和算法的抽象。
行為型模式不僅僅關注類和對象的結構，而且重點關注它們之間的相互作用。
通過行為型模式，可以更加清晰地劃分類與對象的職責，並研究系統在運行時實例對象 之間的交互。在系統運行時，對象並不是孤立的，它們可以通過相互通信與協作完成某些複雜功能，一個對象在運行時也將影響到其他對象的運行。

行為型模式分為類行為型模式和對象行為型模式兩種：

* 類行為型模式

    類的行為型模式使用繼承關係在幾個類之間分配行為，類行為型模式主要通過多態等方式來分配父類與子類的職責。
* 對象行為型模式

    對象的行為型模式則使用對象的聚合關聯關係來分配行為，對象行為型模式主要是通過對象關聯等方式來分配兩個或多個類的職責。根據“合成複用原則”，系統中要儘量使用關聯關係來取代繼承關係，因此大部分行為型設計模式都屬於對象行為型設計模式。

### 代碼結構

-code  上面"23種指針的使用方式"

    Create  5種創建型

    Behavior 11種行為型

    Struct  7種結構型

-Template 用C++模板技巧實現的，個別能複用的設計模式
    
    Create -> SingleTon  
    
    單例模板，繼承模板以實現複用。
    
    c++11的static保證多線程唯一實例, c++17的inline保證創建順序在main之前。
    
    “雙檢測鎖定手法”、Boost那個佔位器單例、《C++設計新思維》那種“鳳凰單例” 都可以被消滅。。。
    
    懶漢模式：需要時才創建，就用static足夠了。
    餓漢模式：main之前創建。static inline足夠了。

    Behavior -> Observer

    觀察者模板，繼承模板以複用。

### 聯繫方式:

***

| 作者 | 濤哥                           |
| ---- | -------------------------------- |
|開發理念 | 弘揚魯班文化，傳承工匠精神 |
| 博客 | https://jaredtao.github.io/ |
|知乎專欄| https://zhuanlan.zhihu.com/TaoQt |
|微信公眾號| Qt進階之路 |
|QQ群| 734623697(高質量群，只能交流技術、分享書籍、幫助解決實際問題）|
| 郵箱 | jared2020@163.com                |
| 微信 | xsd2410421                       |
| QQ、TIM | 759378563                      |
***

QQ(TIM)、微信二維碼

<img src="https://github.com/jaredtao/jaredtao.github.io/blob/master/img/qq_connect.jpg?raw=true" width="30%" height="30%" /><img src="https://github.com/jaredtao/jaredtao.github.io/blob/master/img/weixin_connect.jpg?raw=true" width="30%" height="30%" />


###### 請放心聯繫我，樂於提供諮詢服務，也可洽談有償技術支持相關事宜。

***
#### **打賞**
<img src="https://github.com/jaredtao/jaredtao.github.io/blob/master/img/weixin.jpg?raw=true" width="30%" height="30%" /><img src="https://github.com/jaredtao/jaredtao.github.io/blob/master/img/zhifubao.jpg?raw=true" width="30%" height="30%" />

###### 覺得分享的內容還不錯, 就請作者喝杯奶茶吧~~
***
