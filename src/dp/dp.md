# 設計模式 (Design Patterns)

## 簡介

設計模式是軟體工程中解決常見問題的可重複使用的解決方案。這些模式代表了經過驗證的最佳實踐，由經驗豐富的開發者歸納整理而成。

## 為什麼學習設計模式？

1. **提高程式碼品質**：設計模式幫助建立更加靈活、可維護和可重用的程式碼
2. **改善溝通**：提供開發者之間的共同語言
3. **解決常見問題**：避免重新發明輪子
4. **提升設計能力**：學習前人的經驗和智慧

## 設計模式分類

### 創建型模式 (Creational Patterns)
- **Singleton 單例模式**：確保類別只有一個實例
- **Factory Method 工廠方法模式**：定義創建物件的介面
- **Abstract Factory 抽象工廠模式**：提供創建相關物件家族的介面
- **Builder 建造者模式**：分離複雜物件的建構和表示
- **Prototype 原型模式**：透過複製現有實例創建新物件

### 結構型模式 (Structural Patterns)
- **Adapter 適配器模式**：讓不相容的介面能夠合作
- **Bridge 橋接模式**：將抽象與實現分離
- **Composite 組合模式**：將物件組合成樹狀結構
- **Decorator 裝飾者模式**：動態地給物件添加新功能
- **Facade 外觀模式**：為子系統提供統一的介面
- **Flyweight 享元模式**：共享大量細粒度物件
- **Proxy 代理模式**：為其他物件提供代理或佔位符

### 行為型模式 (Behavioral Patterns)
- **Chain of Responsibility 責任鏈模式**：避免請求發送者與接收者耦合
- **Command 命令模式**：將請求封裝為物件
- **Iterator 迭代器模式**：提供順序訪問集合元素的方法
- **Mediator 中介者模式**：定義物件間的交互方式
- **Memento 備忘錄模式**：在不破壞封裝的前提下捕獲和恢復物件狀態
- **Observer 觀察者模式**：定義物件間的一對多依賴關係
- **State 狀態模式**：允許物件在內部狀態改變時改變行為
- **Strategy 策略模式**：定義一系列演算法並使其可以互換
- **Template Method 模板方法模式**：定義演算法骨架，將某些步驟延遲到子類
- **Visitor 訪問者模式**：將演算法與物件結構分離

## 學習資源

### 經典書籍
1. **《設計模式：可復用物件導向軟體的基礎》** - Gang of Four (GoF)
   - 設計模式的開山之作，定義了 23 個經典設計模式

2. **《Head First 設計模式》**
   - 以輕鬆有趣的方式講解設計模式，適合初學者

3. **《重構：改善既有程式的設計》** - Martin Fowler
   - 講解如何透過重構改善程式碼設計

### 線上資源

1. **Refactoring.Guru**
   - https://refactoring.guru/design-patterns
   - 提供圖解說明和多種程式語言的實現範例

2. **Source Making**
   - https://sourcemaking.com/design_patterns
   - 詳細解釋每個設計模式的應用場景和實現

3. **Design Patterns in Object Oriented Programming**
   - https://www.youtube.com/playlist?list=PLrhzvIcii6GNjpARdnO4ueTUAVR9eMBpc
   - Christopher Okhravi 的 YouTube 系列影片

4. **Java Design Patterns**
   - https://java-design-patterns.com/
   - 用 Java 實現的設計模式集合，開源專案

### 實踐建議

1. **從簡單的模式開始**：如 Singleton、Factory、Observer
2. **理解問題再應用模式**：不要為了用模式而用模式
3. **結合實際專案**：在真實場景中練習和應用
4. **閱讀優秀開源專案**：學習他們如何使用設計模式
5. **重構舊程式碼**：嘗試用設計模式改善現有程式碼

## SOLID 原則

設計模式的基礎是 SOLID 原則：

- **S**ingle Responsibility Principle (單一職責原則)
- **O**pen/Closed Principle (開放封閉原則)
- **L**iskov Substitution Principle (里氏替換原則)
- **I**nterface Segregation Principle (介面隔離原則)
- **D**ependency Inversion Principle (依賴反轉原則)

## 注意事項

1. **避免過度設計**：不是所有問題都需要設計模式
2. **考慮語言特性**：某些模式在特定語言中可能有更簡單的實現
3. **保持簡單**：優先選擇簡單直接的解決方案
4. **持續學習**：設計模式不是終點，而是更好設計的起點

## 相關主題

- 架構模式 (Architectural Patterns)
- 反模式 (Anti-patterns)
- 領域驅動設計 (Domain-Driven Design)
- 微服務模式 (Microservice Patterns)