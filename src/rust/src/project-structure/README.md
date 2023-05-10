# **Rust模塊組織結構**

## **基本說明**

當工程規模變大時，把代碼寫到一個甚至幾個文件中，都是不太聰明的做法，可能存在以下問題：

1.  單個文件過大，導致打開、翻頁速度大幅變慢
2.  查詢和定位效率大幅降低，類比下，你會把所有知識內容放在一個幾十萬字的文檔中嗎？
3.  只有一個代碼層次：函數，難以維護和協作，想象一下你的操作系統只有一個根目錄，剩下的都是單層子目錄會如何：`disaster`

同時，將大的代碼文件拆分成包和模塊，還允許我們實現代碼抽象和複用：將你的代碼封裝好後提供給用戶，那麼用戶只需要調用公共接口即可，無需知道內部該如何實現；

Rust 有自己的規則和約定來組織其模塊；例如：一個 crate 包最多可以有一個庫 `crate`，任意多個二進制`crate`、導入文件夾內的模塊的兩種約定方式等等；

先把一些術語說明一下：

-   項目(Packages)：**一個 `Cargo` 提供的 `feature`，可以用來構建、測試和分享包；**
-   包(Crate)：**一個由多個模塊組成的樹形結構，可以作為三方庫進行分發，也可以生成可執行文件進行運行；**
-   模塊(Module)：**可以一個文件多個模塊，也可以一個文件一個模塊**，模塊可以被認為是真實項目中的代碼組織單元；

首先，`包(crate)` 是 Cargo 中的定義，執行 `cargo new xxxx` 就是創建了一個包，`crate` 是二進制(bin)或庫(lib)項目；

Rust 約定：在 `Cargo.toml` 的同級目錄下：

-   包含`src/main.rs`文件，就是**與包同名的二進制`crate`；**
-   包含`src/lib.rs`，就是與**包同名的庫`crate`；**

一個包內可以有多個 `crate`，多個`crates`就是一個模塊的樹形結構；例如，如果一個包內同時包含`src/main.rs`和`src/lib.rs`，那麼他就有兩個`crate`；

如果想要包含多個二進制`crate`，`rust`規定：需要將文件放在`src/bin`目錄下，每個文件就是一個單獨的`crate`！

`crate root` 是用來描述如何構建`crate`的文件；例如：`src/main.rs`、`src/lib.rs` 都是`crate root`；

**`crate root`將由`Cargo`傳遞給`rustc`來實際構建庫或者二進制項目！**

>   <font color="#f00">**這也是為什麼，入口文件中要寫入各個模塊：`mod xxx;` 才能使其生效！**</font>

**帶有 `Cargo.toml` 文件的包用來整體描述如何構建`crate`；同時，一個包可以最多有一個庫`crate`，任意多個二進制`crate`；**

<br/>

## **Package、Crate和Module**

項目 `Package` 和包 `Crate` 的概念很容易被搞混，甚至在很多書中，這兩者都是不分的，但是由於官方對此做了明確的區分，因此我們會在本章節中試圖(掙扎著)理清這個概念；

### **包 Crate**

對於 Rust 而言，**crate 是一個獨立的可編譯單元，它編譯後會生成一個可執行文件或者一個庫；**

一個包會將相關聯的功能打包在一起，使得該功能可以很方便的在多個項目中分享；

例如：標準庫中沒有提供、而是在三方庫中提供的 `rand` 包；它提供了隨機數生成的功能，我們只需要將該包通過 `use rand;` 引入到當前項目的作用域中，就可以在項目中使用 `rand` 的功能：`rand::XXX`；

**同一個包中不能有同名的類型，但是在不同包中就可以；**例如，雖然 `rand` 包中，有一個 `Rng` 特徵，可是我們依然可以在自己的項目中定義一個 `Rng`，前者通過 `rand::Rng` 訪問，後者通過 `Rng` 訪問，對於編譯器而言，這兩者的邊界非常清晰，不會存在引用歧義；

<br/>

### **項目 Package**

鑑於 Rust 團隊標新立異的起名傳統，以及包的名稱被 `crate` 佔用，庫的名稱被 `library` 佔用，經過斟酌， 我們決定將 `Package` 翻譯成項目，你也可以理解為工程、軟件包；

由於 `Package` 就是一個項目，因此它<font color="#f00">**包含有獨立的 `Cargo.toml` 文件，以及因為功能性被組織在一起的一個或多個包；一個 `Package` 只能包含一個庫(library)類型的包，但是可以包含多個二進制可執行類型的包；**</font>

<br/>

#### **二進制 Package**

下面的命令可以創建一個二進制 `Package`：

```bash
$ cargo new my-project
     Created binary (application) `my-project` package
$ ls my-project
Cargo.toml
src
$ ls my-project/src
main.rs
```

這裡，Cargo 為我們創建了一個名稱是 `my-project` 的 `Package`，同時在其中創建了 `Cargo.toml` 文件，可以看一下該文件，裡面並沒有提到 `src/main.rs` 作為程序的入口；

原因是 Cargo 有一個慣例：<font color="#f00">**`src/main.rs` 是二進制包的根文件，該二進制包的包名跟所屬 `Package` 相同，在這裡都是 `my-project`，所有的代碼執行都從該文件中的 `fn main()` 函數開始；**</font>

使用 `cargo run` 可以運行該項目，輸出：`Hello, world!`；

<br/>

#### **庫 Package**

再來創建一個庫類型的 `Package`：

```bash
$ cargo new my-lib --lib
     Created library `my-lib` package
$ ls my-lib
Cargo.toml
src
$ ls my-lib/src
lib.rs
```

首先，如果你試圖運行 `my-lib`，會報錯：

```bash
$ cargo run
error: a bin target must be available for `cargo run`
```

原因是：<font color="#f00">**庫類型的 `Package` 只能作為三方庫被其它項目引用，而不能獨立運行，只有之前的二進制 `Package` 才可以運行；**</font>

與 `src/main.rs` 一樣，Cargo 知道，如果一個 `Package` 包含有 `src/lib.rs`，意味它包含有一個庫類型的同名包 `my-lib`，該包的根文件是 `src/lib.rs`；

<br/>

#### **易混淆的 Package 和包**

看完上面，相信大家看出來為何 `Package` 和包容易被混淆了吧？因為你用 `cargo new` 創建的 `Package` 和它其中包含的包是同名的！

不過，只要你牢記：**`Package` 是一個項目工程，而包只是一個編譯單元，基本上也就不會混淆這個兩個概念了：`src/main.rs` 和 `src/lib.rs` 都是編譯單元，因此它們都是包；**

<br/>

#### **典型的 `Package` 結構**

上面創建的 `Package` 中僅包含 `src/main.rs` 文件，意味著它僅包含一個二進制同名包 `my-project`；

如果一個 `Package` 同時擁有 `src/main.rs` 和 `src/lib.rs`，那就意味著它包含兩個包：庫包和二進制包；

**同時，這兩個包名也都是 `my-project` —— 都與 `Package` 同名；**

一個真實項目中典型的 `Package`，會包含多個二進制包，這些包文件被放在 `src/bin` 目錄下，每一個文件都是獨立的二進制包，同時也會包含一個庫包，該包只能存在一個 `src/lib.rs`：

```bash
.
├── Cargo.toml
├── Cargo.lock
├── src
│   ├── main.rs
│   ├── lib.rs
│   └── bin
│       └── main1.rs
│       └── main2.rs
├── tests
│   └── some_integration_tests.rs
├── benches
│   └── simple_bench.rs
└── examples
    └── simple_example.rs
```

-   **唯一庫包：`src/lib.rs`**
-   **默認二進制包：`src/main.rs`，編譯後生成的可執行文件與 `Package` 同名**
-   **其餘二進制包：`src/bin/main1.rs` 和 `src/bin/main2.rs`，它們會分別生成一個文件同名的二進制可執行文件**
-   **集成測試文件：`tests` 目錄下**
-   **基準性能測試 `benchmark` 文件：`benches` 目錄下**
-   **項目示例：`examples` 目錄下**

這種目錄結構基本上是 Rust 的標準目錄結構，在 `GitHub` 的大多數項目上，你都將看到它的身影；

理解了包的概念，我們再來看看構成包的基本單元：模塊；

<br/>

### **模塊 Module**

本小節講深入講解 Rust 的代碼構成單元：模塊；

使用模塊可以將包中的代碼按照功能性進行重組，最終實現更好的可讀性及易用性；

同時，我們還能非常靈活地去控制代碼的可見性，進一步強化 Rust 的安全性；

<br/>

#### **創建嵌套模塊**

小餐館，相信大家都挺熟悉的，學校外的估計也沒少去，那麼咱就用小餐館為例，來看看 Rust 的模塊該如何使用；

可以使用 `cargo new --lib restaurant` 創建一個小餐館；

注意，這裡創建的是一個庫類型的 `Package`，然後將以下代碼放入 `src/lib.rs` 中：

```rust
// 餐廳前廳，用於吃飯
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}

        fn seat_at_table() {}
    }

    mod serving {
        fn take_order() {}

        fn serve_order() {}

        fn take_payment() {}
    }
}
```

**以上的代碼（在同一個文件中就）創建了三個模塊**，有幾點需要注意的：

-   **使用 `mod` 關鍵字來創建新模塊，後面緊跟著模塊名稱；**
-   **模塊可以嵌套，這裡嵌套的原因是招待客人和服務都發生在前廳，因此我們的代碼模擬了真實場景；**
-   **模塊中可以定義各種 Rust 類型，例如函數、結構體、枚舉、特徵等；**
-   **所有模塊均定義在同一個文件中；**

類似上述代碼中所做的，使用模塊，我們就能將功能相關的代碼組織到一起，然後通過一個模塊名稱來說明這些代碼為何被組織在一起，這樣其它程序員在使用你的模塊時，就可以更快地理解和上手；

<br/>

#### **模塊樹**

之前我們提到過 `src/main.rs` 和 `src/lib.rs` 被稱為包根(crate root)，是由於這兩個文件的內容形成了一個模塊 `crate`，該模塊位於包的樹形結構(由模塊組成的樹形結構)的根部：

```bash
crate
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
     │   └── seat_at_table
     └── serving
         ├── take_order
         ├── serve_order
         └── take_payment
```

這顆樹展示了模塊之間**彼此的嵌套**關係，因此被稱為**模塊樹**；

其中 `crate` 包根是 `src/lib.rs` 文件，包根文件中的三個模塊分別形成了模塊樹的剩餘部分；

<br/>

##### **父子模塊**

如果模塊 `A` 包含模塊 `B`，那麼 `A` 是 `B` 的父模塊，`B` 是 `A` 的子模塊；

在上例中，`front_of_house` 是 `hosting` 和 `serving` 的父模塊，反之，後兩者是前者的子模塊；

聰明的讀者，應該能聯想到，模塊樹跟計算機上文件系統目錄樹的相似之處；

然而不僅僅是組織結構上的相似，就連使用方式都很相似：**每個文件都有自己的路徑，用戶可以通過這些路徑使用它們，在 Rust 中，我們也通過路徑的方式來引用模塊；**

<br/>

#### **用路徑引用模塊**

想要調用一個函數，就需要知道它的路徑，在 Rust 中，這種路徑有兩種形式：

-   **絕對路徑**，從包根開始，路徑名以包名或者 `crate` 作為開頭
-   **相對路徑**，從當前模塊開始，以 `self`，`super` 或當前模塊的標識符作為開頭

讓我們繼續經營那個慘淡的小餐館，這次為它實現一個小功能：

src/lib.rs

```rust
// 餐廳前廳，用於吃飯
pub mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    // 絕對路徑
    crate::front_of_house::hosting::add_to_waitlist();

    // 相對路徑
    front_of_house::hosting::add_to_waitlist();
}
```

`eat_at_restaurant` 是一個定義在 crate root 中的函數，在該函數中使用了兩種方式對 `add_to_waitlist` 進行調用；

##### **絕對路徑引用**

因為 `eat_at_restaurant` 和 `add_to_waitlist` 都定義在一個包中，因此在絕對路徑引用時，可以直接以 `crate` 開頭，然後逐層引用，每一層之間使用 `::` 分隔：

```rust
crate::front_of_house::hosting::add_to_waitlist();
```

對比下之前的模塊樹：

```bash
crate
 └── eat_at_restaurant
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
     │   └── seat_at_table
     └── serving
         ├── take_order
         ├── serve_order
         └── take_payment
```

可以看出，絕對路徑的調用，完全符合了模塊樹的層級遞進，非常符合直覺；

如果類比文件系統，就跟使用絕對路徑調用可執行程序差不多：`/front_of_house/hosting/add_to_waitlist`，使用 `crate` 作為開始就和使用 `/` 作為開始一樣；

<br/>

##### **相對路徑引用**

再回到模塊樹中，因為 `eat_at_restaurant` 和 `front_of_house` 都處於 `crate root` 中，因此相對路徑可以使用 `front_of_house` 作為開頭：

```rust
front_of_house::hosting::add_to_waitlist();
```

如果類比文件系統，那麼它**類似於調用同一個目錄下的程序**，你可以這麼做：`front_of_house/hosting/add_to_waitlist`；

<br/>

##### **絕對還是相對？**

**如果只是為了引用到指定模塊中的對象，那麼兩種都可以；**

但是在實際使用時，需要遵循一個原則：<font color="#f00">**當代碼被挪動位置時，儘量減少引用路徑的修改，相信大家都遇到過，修改了某處代碼，導致所有路徑都要挨個替換，這顯然不是好的路徑選擇；**</font>

回到之前的例子：

如果我們把 `front_of_house` 模塊和 `eat_at_restaurant` 移動到一個模塊中 `customer_experience`，那麼絕對路徑的引用方式就必須進行修改：`crate::customer_experience::front_of_house ...`；

但是假設我們使用的相對路徑，那麼該路徑就無需修改，因為它們兩個的相對位置其實沒有變：

```console
crate
 └── customer_experience
    └── eat_at_restaurant
    └── front_of_house
        ├── hosting
        │   ├── add_to_waitlist
        │   └── seat_at_table
```

從新的模塊樹中可以很清晰的看出這一點；

再比如，其它的都不動，把 `eat_at_restaurant` 移動到模塊 `dining` 中，如果使用相對路徑，你需要修改該路徑，但如果使用的是絕對路徑，就無需修改：

```console
crate
 └── dining
     └── eat_at_restaurant
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
```

不過，如果不確定哪個好，你可以考慮**優先使用絕對路徑，因為調用的地方和定義的地方往往是分離的，而定義的地方較少會變動；**

<br/>

#### **代碼可見性**

Rust 出於安全的考慮，默認情況下，所有的類型都是私有化的，包括函數、方法、結構體、枚舉、常量，是的，就連模塊本身也是私有化的；

在 Rust 中，**父模塊`完全無法訪問`子模塊中的私有項，但是子模塊卻可以訪問父模塊、父父..模塊的私有項！**

例如下面的代碼是無法編譯通過的：

```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    // 絕對路徑
    crate::front_of_house::hosting::add_to_waitlist();

    // 相對路徑
    front_of_house::hosting::add_to_waitlist();
}
```

`hosting` 模塊是私有的，無法在包根進行訪問；

那麼為何 `front_of_house` 模塊就可以訪問？

因為它和 `eat_at_restaurant` 同屬於一個包根作用域內，**同一個模塊內的代碼自然不存在私有化問題**(所以我們之前章節的代碼都沒有報過這個錯誤！)；

類似其它語言的 `public` 或者 Go 語言中的首字母大寫，Rust 提供了 `pub` 關鍵字，通過它你可以控制模塊和模塊中指定項的可見性；

<br/>

#### **使用 `super` 引用模塊**

在上文用路徑引用模塊小節，使用路徑引用模塊中，我們提到了相對路徑有三種方式開始：`self`、`super`和 `crate` 或者模塊名，其中第三種在前面已經講到過，現在來看看通過 `super` 的方式引用模塊項；

`super` 代表的是**父模塊為開始的引用方式，非常類似於文件系統中的 `..`；**

語法：`../a/b` 文件名：

src/lib.rs

```rust
// 餐廳前廳，用於吃飯
pub mod front_of_house {
    pub mod serving {
        fn serve_order() {}

        // 廚房模塊
        mod back_of_house {
            fn fix_incorrect_order() {
                cook_order();
                super::serve_order();
            }

            fn cook_order() {}
        }
    }
}
```

在廚房模塊中，使用 `super::serve_order` 語法，調用了父模塊中的 `serve_order` 函數；

那麼你可能會問，為何不使用 `crate::serve_order` 的方式？

其實也可以，不過如果你確定未來這種層級關係不會改變，那麼 `super::serve_order` 的方式會更穩定，未來就算它們都不在 crate root了，依然無需修改引用路徑；

所以路徑的選用，往往還是取決於場景，以及未來代碼的可能走向；

<br/>

#### **使用 `self` 引用模塊**

`self` 其實就是引用自身模塊中的項，也就是說和我們之前章節的代碼類似，都調用同一模塊中的內容，區別在於之前章節中直接通過名稱調用即可，而 `self`，你得多此一舉：

```rust
pub mod serving {

  fn serve_order() {
    self::back_of_house::cook_order()
  }

  // 廚房模塊
  mod back_of_house {
    pub fn cook_order() {}
  }
}
```

是的，多此一舉，因為完全可以直接調用 `back_of_house`，但是 `self` 還有一個大用處，在後文中會講；

<br/>

#### **結構體和枚舉的可見性**

為何要把結構體和枚舉的可見性單獨拎出來講呢？因為這兩個傢伙的成員字段擁有完全不同的可見性：

-   **將結構體設置為 `pub`，但它的所有字段依然是私有的；**
-   **將枚舉設置為 `pub`，它的所有字段則將對外可見；**

原因在於：**枚舉和結構體的使用方式不一樣：**

-   如果枚舉的成員對外不可見，那該枚舉將一點用都沒有，因此枚舉成員的可見性自動跟枚舉可見性保持一致，這樣可以簡化用戶的使用；
-   而結構體的應用場景比較複雜，其中的字段也往往部分在 A 處被使用，部分在 B 處被使用，因此無法確定成員的可見性，那索性就設置為全部不可見，將選擇權交給程序員；

<br/>

#### **模塊與文件分離**

在之前的例子中，我們所有的模塊都定義在 `src/lib.rs` 中，但是當模塊變多或者變大時，需要**將模塊放入一個單獨的文件中**，讓代碼更好維護；

現在，把 `front_of_house` 前廳分離出來，放入一個單獨的文件中：

src/front_of_house.rs

```rust
// 餐廳前廳，用於吃飯
pub mod hosting {
    pub fn add_to_waitlist() {}

    fn seat_at_table() {}
}

pub mod serving {
    fn take_order() {}

    fn serve_order() {
        self::back_of_house::cook_order()
    }

    fn take_payment() {}

    // 廚房模塊
    mod back_of_house {
        fn fix_incorrect_order() {
            cook_order();
            super::serve_order();
        }

        pub fn cook_order() {}
    }
}
```

然後，將以下代碼留在 `src/lib.rs` 中：

```rust
mod front_of_house;

pub use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    // 絕對路徑
    hosting::add_to_waitlist();

    // 相對路徑
    hosting::add_to_waitlist();
}
```

其實跟之前在同一個文件中也沒有太大的不同，但是有幾點值得注意：

-   `mod front_of_house`：告訴 Rust 從另一個和模塊 `front_of_house` 同名的文件中加載該模塊的內容；
-   使用絕對路徑的方式來引用 `hosting` 模塊：`crate::front_of_house::hosting`；

需要注意的是，和之前代碼中 `mod front_of_house{..}` 的完整模塊不同：

現在的代碼中，**模塊的聲明和實現是分離的**，實現是在單獨的 `front_of_house.rs` 文件中，然後通過 `mod front_of_house;` 這條聲明語句從該文件中把模塊內容加載進來；

**因此我們可以認為：模塊 `front_of_house` 的定義還是在 `src/lib.rs` 中，只不過模塊的具體內容被移動到了 `src/front_of_house.rs` 文件中；**

在這裡出現了一個新的關鍵字 `use`，聯想到其它章節我們見過的標準庫引入 `use std::fmt;`，可以大致猜測，該關鍵字**用來將外部模塊中的項引入到當前作用域中來，這樣無需冗長的父模塊前綴即可調用**：`hosting::add_to_waitlist();`，在下節中，我們將對 `use` 進行詳細的講解；

<br/>

## **使用 use 及受限可見性**

如果代碼中，通篇都是 `crate::front_of_house::hosting::add_to_waitlist` 這樣的函數調用形式，我不知道有誰會喜歡；

因此我們需要一個辦法來簡化這種使用方式，在 Rust 中，**可以使用 `use` 關鍵字把路徑提前引入到當前作用域中，隨後的調用就可以省略該路徑，極大地簡化了代碼；**

<br/>

### **基本引入方式**

在 Rust 中，引入模塊中的項有兩種方式：[絕對路徑和相對路徑](https://course.rs/basic/crate-module/module.html#用路徑引用模塊)，這兩者在前文中都講過，就不再贅述；

先來看看使用絕對路徑的引入方式；

#### **絕對路徑引入模塊**

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
}
```

這裡，我們使用 `use` 和絕對路徑的方式，將 `hosting` 模塊引入到當前作用域中，然後只需通過 `hosting::add_to_waitlist` 的方式，即可調用目標模塊中的函數；

相比 `crate::front_of_house::hosting::add_to_waitlist()` 的方式要簡單的多；

那麼，還能更簡單嗎？

<br/>

#### **相對路徑引入模塊中的函數**

在下面代碼中，我們不僅要使用相對路徑進行引入，而且與上面引入 `hosting` 模塊不同，直接引入該模塊中的 `add_to_waitlist` 函數：

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

use front_of_house::hosting::add_to_waitlist;

pub fn eat_at_restaurant() {
    add_to_waitlist();
    add_to_waitlist();
    add_to_waitlist();
}
```

很明顯，函數調用又變得更短了；

<br/>

#### **引入模塊還是函數？**

從使用簡潔性來說，引入函數自然是更甚一籌，但是在某些時候，引入模塊會更好：

-   **需要引入同一個模塊的多個函數**
-   **作用域中存在同名函數**

在以上兩種情況中，使用 `use front_of_house::hosting` 引入模塊要比 `use front_of_house::hosting::add_to_waitlist;` 引入函數更好；

**例如，如果想使用 `HashMap`，那麼直接引入該結構體是比引入模塊更好的選擇，因為在 `collections` 模塊中，我們只需要使用一個 `HashMap` 結構體：**

```rust
use std::collections::HashMap;

fn main() {
    let mut map = HashMap::new();
    map.insert(1, 2);
}
```

其實嚴格來說，對於引用方式並沒有需要遵守的慣例，主要還是取決於你的喜好，不過我們建議：

**優先使用最細粒度(引入函數、結構體等)的引用方式，如果引起了某種麻煩(例如前面兩種情況)，再使用引入模塊的方式；**

<br/>

### **避免同名引用**

根據上一章節的內容，我們只要**保證同一個模塊中不存在同名項**就行；

話雖如此，一起看看，如果遇到同名的情況該如何處理；

#### **模塊::函數**

```rust
use std::fmt;
use std::io;

fn function1() -> fmt::Result {
    // --snip--
}

fn function2() -> io::Result<()> {
    // --snip--
}
```

上面的例子給出了很好的解決方案，使用模塊引入的方式，具體的 `Result` 通過 `模塊::Result` 的方式進行調用；

可以看出，**避免同名衝突的關鍵，就是使用父模塊的方式來調用；**

除此之外，還可以給予引入的項起一個別名；

<br/>

#### **`as` 別名引用**

對於同名衝突問題，還可以使用 `as` 關鍵字來解決，它可以賦予引入項一個全新的名稱：

```rust
use std::fmt::Result;
use std::io::Result as IoResult;

fn function1() -> Result {
    // --snip--
}

fn function2() -> IoResult<()> {
    // --snip--
}
```

如上所示，首先通過 `use std::io::Result` 將 `Result` 引入到作用域，然後使用 `as` 給予它一個全新的名稱 `IoResult`，這樣就不會再產生衝突：

-   `Result` 代表 `std::fmt::Result；`
-   `IoResult` 代表 `std:io::Result`；

<br/>

### **引入項再導出**

**當外部的模塊項 `A` 被引入到當前模塊中時，它的可見性自動被設置為私有的，如果你希望允許其它外部代碼引用我們的模塊項 `A`，那麼可以對它進行再導出：**

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub use crate::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
}
```

如上，**使用 `pub use` 即可實現：**

**這裡 `use` 代表引入 `hosting` 模塊到當前作用域，`pub` 表示將該引入的內容再度設置為可見；**

當你希望將內部的實現細節隱藏起來或者按照某個目的組織代碼時，可以使用 `pub use` 再導出；

例如，統一使用一個模塊來提供對外的 API，那該模塊就可以引入其它模塊中的 API，然後進行再導出，最終對於用戶來說，所有的 API 都是由一個模塊統一提供的；

<br/>

## **使用第三方包**

之前我們一直在引入標準庫模塊或者自定義模塊，現在來引入下第三方包中的模塊；

關於如何引入外部依賴，在 [Cargo 入門](https://course.rs/first-try/cargo.html#package-配置段落)中就有講，這裡直接給出操作步驟：

1.  **修改 `Cargo.toml` 文件，在 `[dependencies]` 區域添加一行：`rand = "0.8.3"`**
2.  **此時，如果你用的是 `VSCode` 和 `rust-analyzer` 插件，該插件會自動拉取該庫，你可能需要等它完成後，再進行下一步（VSCode 左下角有提示）**

好了，此時，`rand` 包已經被我們添加到依賴中，下一步就是在代碼中使用：

```rust
use rand::Rng;

fn main() {
    let secret_number = rand::thread_rng().gen_range(1..101);
}
```

這裡使用 `use` 引入了第三方包 `rand` 中的 `Rng` 特徵，因為我們需要調用的 `gen_range` 方法定義在該特徵中；

>   **crates.io，lib.rs**
>
>   Rust 社區已經為我們貢獻了大量高質量的第三方包，你可以在 `crates.io` 或者 `lib.rs` 中檢索和使用；
>
>   從目前來說查找包更推薦 `lib.rs`，搜索功能更強大，內容展示也更加合理，但是下載依賴包還是得用`crates.io`；

<br/>

## **使用 `{}` 簡化引入方式**

對於以下一行一行的引入方式：

```rust
use std::collections::HashMap;
use std::collections::BTreeMap;
use std::collections::HashSet;

use std::cmp::Ordering;
use std::io;
```

可以使用 `{}` 來一起引入進來，在大型項目中，使用這種方式來引入，可以減少大量 `use` 的使用：

```rust
use std::collections::{HashMap,BTreeMap,HashSet};
use std::{cmp::Ordering, io};
```

對於下面的同時引入模塊和模塊中的項：

```rust
use std::io;
use std::io::Write;
```

可以使用 `{}` 的方式進行簡化:

```rust
use std::io::{self, Write};
```

>   **self**
>
>   上面使用到了模塊章節提到的 `self` 關鍵字，用來替代模塊自身，結合上一節中的 `self`，可以得出它在模塊中的兩個用途：
>
>   -   **`use self::xxx`，表示加載當前模塊中的 `xxx`。此時 `self` 可省略**
>   -   **`use xxx::{self, yyy}`，表示，加載當前路徑下模塊 `xxx` 本身，以及模塊 `xxx` 下的 `yyy`**

<br/>

## **使用 `*` 引入模塊下的所有項**

對於之前一行一行引入 `std::collections` 的方式，我們還可以使用

```rust
use std::collections::*;
```

以上這種方式來引入 `std::collections` 模塊下的所有公共項，這些公共項自然包含了 `HashMap`，`HashSet` 等想手動引入的集合類型；

當**使用 `*` 來引入的時候要格外小心，因為你很難知道到底哪些被引入到了當前作用域中，有哪些會和你自己程序中的名稱相沖突：**

```rust
use std::collections::*;

struct HashMap;
fn main() {
   let mut v =  HashMap::new();
   v.insert("a", 1);
}
```

以上代碼中，`std::collection::HashMap` 被 `*` 引入到當前作用域，但是由於存在另一個同名的結構體，因此 `HashMap::new` 根本不存在，因為對於編譯器來說，**本地同名類型的優先級更高；**

在實際項目中，**這種引用方式往往用於快速寫測試代碼，它可以把所有東西一次性引入到 `tests` 模塊中；**

<br/>

## **其他引入模塊的方式**

通過 `#[path ="你的路徑"]` 可以放在任何目錄都行，如：

```rust
#[path ="你的路徑"]
mod core;
```

可以無視 `mod.rs` 或者目錄方式：

[![image](https://user-images.githubusercontent.com/100085326/164968138-0efae930-8bc0-4c8b-b4e8-163e6c566d5a.png)](https://user-images.githubusercontent.com/100085326/164968138-0efae930-8bc0-4c8b-b4e8-163e6c566d5a.png)

當然，也可以在目錄下創建 `mod.rs` 文件，但是需要一層一層的 `pub mod` 導出，或者採用 `2018` 版本的模塊目錄和模塊.rs 同名方式（**官方推薦**)，總之，`#[path]` 方式最靈活（慎用）；

三種方式對比：

`Rust` 模塊引用三種方式：

| Rust 2015                                                    | Rust 2018                                                    | #[path = "路徑"]                                             |
| :----------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| .<br/>├── lib.rs<br/>└── foo/<br/>    ├── mod.rs<br/>    └── bar.rs | .<br/>├── lib.rs<br/>├── foo.rs<br/>└── foo/<br/>    └── bar.rs | .<br/>├── lib.rs       <br/>└── pkg/         // 任意目錄名<br/>    ├── foo.rs   // #[path = "./pkg/foo.rs"]<br/>    └── bar.rs   // #[path = "./pkg/bar.rs"] |

<br/>

## **受限的可見性**

在上一節中，我們學習了[可見性](https://course.rs/basic/crate-module/module.html#代碼可見性)這個概念，這也是模塊體系中最為核心的概念，控制了模塊中哪些內容可以被外部看見，但是在實際使用時，光被外面看到還不行，我們還想控制哪些人能看，這就是 Rust 提供的受限可見性；

例如，**在 Rust 中，包是一個模塊樹，我們可以通過 `pub(crate) item;` 這種方式來實現：`item` 雖然是對外可見的，但是隻在當前包內可見，外部包無法引用到該 `item`；**

所以，如果我們想要**讓某一項可以在整個包中都可以被使用，那麼有兩種辦法：**

-   **在crate root中定義一個非 `pub` 類型的 `X`(父模塊的項對子模塊都是可見的，因此包根中的項對模塊樹上的所有模塊都可見)；**
-   **在子模塊中定義一個 `pub` 類型的 `Y`，同時通過 `use` 將其引入到包根；**

例如：

```rust
mod a {
    pub mod b {
        pub fn c() {          
            println!("{:?}",crate::X);
        }

      // 在子模塊中定義一個 `pub` 類型的 `Y`，同時通過 `use` 將其引入到包根
        #[derive(Debug)]
        pub struct Y;
    }
}

// 在crate root中定義一個非 `pub` 類型的 `X`(父模塊的項對子模塊都是可見的，因此包根中的項對模塊樹上的所有模塊都可見)
#[derive(Debug)]
struct X;
use a::b::Y;
fn d() {
    println!("{:?}",Y);
}
```

以上代碼充分說明瞭之前兩種辦法的使用方式，但是有時我們會遇到這兩種方法都不太好用的時候；

例如希望對於某些特定的模塊可見，但是對於其他模塊又不可見：

```rust
// 目標：`a` 導出 `I`、`bar` and `foo`，其他的不導出
pub mod a {
    pub const I: i32 = 3;

    fn semisecret(x: i32) -> i32 {
        use self::b::c::J;
        x + J
    }

    pub fn bar(z: i32) -> i32 {
        semisecret(I) * z
    }
    pub fn foo(y: i32) -> i32 {
        semisecret(I) + y
    }

    mod b {
        mod c {
            const J: i32 = 4;
        }
    }
}
```

這段代碼會報錯，因為與父模塊中的項對子模塊可見相反，子模塊中的項對父模塊是不可見的；

這裡 `semisecret` 方法中，`a` -> `b` -> `c` 形成了父子模塊鏈，那 `c` 中的 `J` 自然對 `a` 模塊不可見；

如果使用之前的可見性方式，那麼想保持 `J` 私有，同時讓 `a` 繼續使用 `semisecret` 函數的辦法是：將該函數移動到 `c` 模塊中，然後用 `pub use` 將 `semisecret` 函數進行再導出：

```rust
pub mod a {
    pub const I: i32 = 3;

    use self::b::semisecret;

    pub fn bar(z: i32) -> i32 {
        semisecret(I) * z
    }
    pub fn foo(y: i32) -> i32 {
        semisecret(I) + y
    }

    mod b {
        pub use self::c::semisecret;
        mod c {
            const J: i32 = 4;
            pub fn semisecret(x: i32) -> i32 {
                x + J
            }
        }
    }
}
```

這段代碼說實話問題不大，但是有些破壞了我們之前的邏輯；

如果想保持代碼邏輯，同時又只讓 `J` 在 `a` 內可見該怎麼辦？

```rust
pub mod a {
    pub const I: i32 = 3;

    fn semisecret(x: i32) -> i32 {
        use self::b::c::J;
        x + J
    }

    pub fn bar(z: i32) -> i32 {
        semisecret(I) * z
    }
    pub fn foo(y: i32) -> i32 {
        semisecret(I) + y
    }

    mod b {
        pub(in crate::a) mod c {
            pub(in crate::a) const J: i32 = 4;
        }
    }
}
```

通過 `pub(in crate::a)` 的方式，我們指定了模塊 `c` 和常量 `J` 的可見範圍都只是 `a` 模塊中，`a` 之外的模塊是完全訪問不到它們的！

<br/>

#### **限制可見性語法**

`pub(crate)` 或 `pub(in crate::a)` 就是限制可見性語法，前者是限制在整個包內可見，後者是通過絕對路徑，**限制在包內的某個模塊內可見**，總結一下：

-   **`pub` 意味著可見性無任何限制；**
-   **`pub(crate)` 表示在當前包可見；**
-   **`pub(self)` 在當前模塊可見；**
-   **`pub(super)` 在父模塊可見；**
-   **`pub(in <path>)` 表示在某個路徑代表的模塊中可見，其中 `path` 必須是父模塊或者祖先模塊；**

<br/>

## **一個單文件多模塊的使用案例**

下面是一個模塊的綜合例子：

my_mod/src/lib.rs

```rust
// 一個名為 `my_mod` 的模塊
mod my_mod {
    // 模塊中的項默認具有私有的可見性
    fn private_function() {
        println!("called `my_mod::private_function()`");
    }

    // 使用 `pub` 修飾語來改變默認可見性。
    pub fn function() {
        println!("called `my_mod::function()`");
    }

    // 在同一模塊中，項可以訪問其它項，即使它是私有的。
    pub fn indirect_access() {
        print!("called `my_mod::indirect_access()`, that\n> ");
        private_function();
    }

    // 模塊也可以嵌套
    pub mod nested {
        pub fn function() {
            println!("called `my_mod::nested::function()`");
        }

        fn private_function() {
            println!("called `my_mod::nested::private_function()`");
        }

        // 使用 `pub(in path)` 語法定義的函數只在給定的路徑中可見。
        // `path` 必須是父模塊（parent module）或祖先模塊（ancestor module）
        pub(in crate::my_mod) fn public_function_in_my_mod() {
            print!("called `my_mod::nested::public_function_in_my_mod()`, that\n > ");
            public_function_in_nested()
        }

        // 使用 `pub(self)` 語法定義的函數則只在當前模塊中可見。
        pub(self) fn public_function_in_nested() {
            println!("called `my_mod::nested::public_function_in_nested");
        }

        // 使用 `pub(super)` 語法定義的函數只在父模塊中可見。
        pub(super) fn public_function_in_super_mod() {
            println!("called my_mod::nested::public_function_in_super_mod");
        }
    }

    pub fn call_public_function_in_my_mod() {
        print!("called `my_mod::call_public_funcion_in_my_mod()`, that\n> ");
        nested::public_function_in_my_mod();
        print!("> ");
        nested::public_function_in_super_mod();
    }

    // `pub(crate)` 使得函數只在當前包中可見
    pub(crate) fn public_function_in_crate() {
        println!("called `my_mod::public_function_in_crate()");
    }

    // 嵌套模塊的可見性遵循相同的規則
    mod private_nested {
        pub fn function() {
            println!("called `my_mod::private_nested::function()`");
        }
    }
}

fn function() {
    println!("called `function()`");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn main() {
        // 模塊機制消除了相同名字的項之間的歧義。
        function();
        my_mod::function();

        // 公有項，包括嵌套模塊內的，都可以在父模塊外部訪問。
        my_mod::indirect_access();
        my_mod::nested::function();
        my_mod::call_public_function_in_my_mod();

        // pub(crate) 項可以在同一個 crate 中的任何地方訪問
        my_mod::public_function_in_crate();

        // pub(in path) 項只能在指定的模塊中訪問
        // 報錯！函數 `public_function_in_my_mod` 是私有的
        //my_mod::nested::public_function_in_my_mod();

        // 模塊的私有項不能直接訪問，即便它是嵌套在公有模塊內部的

        // 報錯！`private_function` 是私有的
        //my_mod::private_function();

        // 報錯！`private_function` 是私有的
        //my_mod::nested::private_function();

        // 報錯！ `private_nested` 是私有的
        //my_mod::private_nested::function();
    }
}
```

>   **上面的內容90%以上整理自：**
>
>   -   https://course.rs/basic/crate-module/intro.html
>
>   **一本神一樣的 Rust 語言聖經！**

<br/>

## **多個目錄間模塊引用**

前面給出的例子大多都是在單個模塊中引用；

本小節來看一看在不同目錄之間的引用；

看一下目錄結構：

```bash
$ tree .                      
.
├── Cargo.lock
├── Cargo.toml
└── src
    ├── main.rs
    └── user_info
        ├── mod.rs
        └── user.rs

3 directories, 9 files
```

**`rust`約定在目錄下使用`mod.rs`將模塊導出；**

看一下user.rs的代碼：

```rust
#[derive(Debug)]
pub struct User {
    name: String,
    age: i32
}

impl User {
    pub fn new_user(name: String, age: i32) -> User {
        User{
            name,
            age
        }
    }
    pub fn name(&self) -> &str {
        &self.name
    }
}

pub fn add(x: i32, y: i32) -> i32 {
    x + y 
}
```

然後在`mod.rs`裡導出：

```rust
pub mod user;
```

在`main.rs`調用：

```rust
mod user_info;
use user_info::user::User;

fn main() {
    let u1 = User::new_user(String::from("tom"), 5);
    println!("user name: {}", u1.name());
    println!("1+2: {}", user_info::user::add(1, 2));
}
```

<br/>

## **多個Cargo之間進行引用**

最後，再來看看多個 Cargo 項目之間的引用；

首先分別創建一個可執行項目和一個庫項目：

```bash
cargo new multi-crate
cargo new utils --lib
```

在utils庫中，已經生成了代碼：

```rust
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

在我們的二進制庫的`Cargo.toml`引入該庫：

```toml
[dependencies]
utils = { path = "../utils", version = "0.1.0" }
```

`path`就是庫項目的路徑；

`main.rs`使用`use`引入就可以使用了：

```rust
use utils::add;

fn main() {
    let x = add(1, 2);
    println!("utils::add(1, 2): {}", x);
}
```

<br/>

# **附錄**

源代碼：

-   https://github.com/JasonkayZK/rust-learn/tree/project-structure

文章參考：

-   https://course.rs/basic/crate-module/intro.html
-   https://www.cnblogs.com/li-peng/p/13587910.html
-   https://stackoverflow.com/questions/67617824/when-to-use-crate-vs-proj-name-in-imports
