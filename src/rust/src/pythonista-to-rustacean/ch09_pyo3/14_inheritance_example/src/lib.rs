//!
//! # PyO3 繼承範例：子類別與父類別的溝通
//!
//! 本範例展示如何在 PyO3 中實現 Python-style 繼承關係，
//! 包括方法覆寫 (override) 與跨層級的屬性存取。
//!
//! ## 架構圖
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────┐
//! │                        Food (父類別)                        │
//! │  ┌─────────────────────────────────────────────────────┐   │
//! │  │ name: String                                        │   │
//! │  │ ─────────────────────────────────────────────────── │   │
//! │  │ + new(name) -> Self                                │   │
//! │  │ + consume()                                         │   │
//! │  └─────────────────────────────────────────────────────┘   │
//! └──────────────────────────┬──────────────────────────────┘
//!                            │ extends (繼承)
//!                            ▼
//! ┌─────────────────────────────────────────────────────────────┐
//! │              Pizza / Pizza2 (子類別)                        │
//! │  ┌─────────────────────────────────────────────────────┐   │
//! │  │ size: String                                        │   │
//! │  │ ─────────────────────────────────────────────────── │   │
//! │  │ + new(name, size) -> PyClassInitializer<Self>      │   │
//! │  │ + description() -> String                          │   │
//! │  │ + consume()  ← 覆寫父類別方法                        │   │
//! │  └─────────────────────────────────────────────────────┘   │
//! │                            │                               │
//! │                            │ extends (多層繼承)              │
//! │                            ▼                               │
//! │  ┌─────────────────────────────────────────────────────┐   │
//! │  │           MargheritaPizza (孫類別)                  │   │
//! │  │  has_basil: bool                                   │   │
//! │  │  ─────────────────────────────────────────────────  │   │
//! │  │  + new(name, size, has_basil) -> PyClassInitializer │   │
//! │  └─────────────────────────────────────────────────────┘   │
//! └─────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 概念              | Python 写法                        | Rust/PyO3 写法                              |
//! |-------------------|------------------------------------|---------------------------------------------|
//! | 定義父類別        | `class Food:`                      | `#[pyclass(subclass)] struct Food`          |
//! | 定義子類別        | `class Pizza(Food):`               | `#[pyclass(subclass, extends=Food)]`        |
//! | 建構子（法一）    | `def __init__(self, name, size):` | `fn new(...) -> PyClassInitializer<Self>`   |
//! | 建構子（法二）    | 同上                              | `fn new(...) -> (Self, Food)` (元組寫法)    |
//! | 存取父類別屬性    | `self.name`                        | `self_.as_super().name`                      |
//! | 覆寫方法          | `def consume(self):`               | `fn consume(self_: PyRef<'_, Self>)`         |
//! | 呼叫父類別方法    | `super().consume()`                | `self_.as_super().consume()`                  |
//!
//! ## 關鍵 PyO3 技法
//!
//! - `#[pyclass(subclass)]`：標註父類別，預留 `extends` 擴充空間
//! - `#[pyclass(subclass, extends=Food)]`：宣告子類別需填入父類別欄位
//! - `PyClassInitializer::from(food).add_subclass(pizza)`：手動組裝繼承鏈
//! - `(Self { size }, Food::new(name))`：元組寫法，PyO3 自動轉換
//! - `self_.as_super()`：取得父類別的 `PyRef`，用於方法覆寫情境
//!
//! ## 使用方式
//!
//! ```python
//! from inheritance_example import Food, Pizza, Pizza2, MargheritaPizza
//!
//! # 基本用法
//! food = Food("Banana")
//! food.consume()  # "Eating Banana!"
//!
//! # 子類別
//! pizza = Pizza("Margherita", "12")
//! print(pizza.description())  # "This is a 12-inch Margherita pizza!"
//! pizza.consume()
//! # Let's get a drink before eating...
//! # Eating Margherita!
//!
//! # 多層繼承
//! margherita = MargheritaPizza("Margherita Special", "10", True)
//! ```
//!
use pymodule mod inheritance_example {

    // 1. 在父類別 Food 加上 subclass 屬性，
    //    告訴 PyO3 它未來可能會被繼承。
    #[pyclass(subclass)]
    struct Food {
        name: String,
    }

    #[pymethods]
    impl Food {
        #[new]
        fn new(name: String) -> Self {
            Food { name }
        }

        fn consume(&self) {
            println!("Eating {}!", self.name)
        }
    }

    // 2. 在子類別 Pizza 使用 extends=Food 宣告繼承關係
    #[pyclass(subclass, extends=Food)]
    struct Pizza {
        size: String,
    }

    #[pymethods]
    impl Pizza {
        // 3. 子類別的建構子，回傳 PyClassInitializer 這份「說明書」
        #[new]
        fn new(name: String, size: String) -> PyClassInitializer<Self> {
            // 先備好父類別這個零件
            let food = Food::new(name);
            // 再備好子類別自己的零件
            let pizza = Pizza { size };
            // 用 PyClassInitializer 將零件打包回傳，交給 PyO3 組裝
            PyClassInitializer::from(food).add_subclass(pizza)
        }

        fn description(self_: PyRef<'_, Self>) -> String {
            // 透過 as_super() 取得父類別的參考
            let food_part = self_.as_super();
            // 現在，我們既可以存取父類別的 name，也可以存取子類別自己的 size
            format!("This is a {}-inch {} pizza!", self_.size, food_part.name)
        }

        // 在子類別中，定義同名方法來「覆寫」
        fn consume(self_: PyRef<'_, Self>) {
            // 這是子類別自己新增的邏輯
            println!("Let's get a drink before eating...");

            // 透過 as_super() 呼叫父類別的 consume
            self_.as_super().consume();
        }
    }

    // 定義另一個子類別 Pizza2，展示另一種寫法
    #[pyclass(extends=Food)]
    struct Pizza2 {
        size: String,
    }

    #[pymethods]
    impl Pizza2 {
        // Pizza2 的建構子（方法二）
        // PyO3 為 (子類別, 父類別) 元組實作了 Into<PyClassInitializer>
        // 所以可以直接回傳元組，會自動轉換為 PyClassInitializer
        #[new]
        fn new(name: String, size: String) -> (Self, Food) {
            // 回傳 (子類別實例, 父類別實例) 元組
            // PyO3 會自動將此元組轉換為正確的繼承結構
            (Self { size }, Food::new(name))
        }
    }

    #[pyclass(extends=Pizza)]
    struct MargheritaPizza {
        has_basil: bool,
    }

    #[pymethods]
    impl MargheritaPizza {
        #[new]
        fn new(name: String, size: String, has_basil: bool) -> PyClassInitializer<Self> {
            // 1. 先建立上一層的「誕生說明書」（Pizza，它內部會處理好 Food）
            let pizza = Pizza::new(name, size);
            // 2. 再建立自己的物件
            let margherita = Self { has_basil };
            // 3. 把自己加到繼承鏈的頂端，形成一份更完整的說明書
            PyClassInitializer::from(pizza).add_subclass(margherita)
        }
    }
}
