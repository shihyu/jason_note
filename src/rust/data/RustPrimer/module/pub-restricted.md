# pub restricted

## 概覽

這是 rust1.18 新增的一個語法。在此之前的版本，`item` 只有 `pub`/non-`pub` 兩種分類，pub restricted 這個語法用來擴展 `pub` 的使用，使其能夠指定想要的作用域\(可見範圍\)，詳情參見RFC [1422-pub-restricted.md](https://github.com/rust-lang/rfcs/blob/master/text/1422-pub-restricted.md)。

在 Rust 中 `crate` 是一個模塊樹，可以通過表達式 `pub(crate) item;` 來限制 `item` 只在當前 `crate` 中可用，在當前 `crate` 的其他子樹中，可以通過 `use + path` 的語法來引用 `item`。

## 設計動因

Rust1.18 之前，如果我們想要設計一個 item `x` 可以在多處使用，那麼有兩種方法：

* 在根目錄中定義一個非 `pub` item；
* 在子模塊中定義一個 `pub` item，同時通過 `use` 將這個項目引用到根目錄。 

但是，有時候這兩種方法都並不是我們想要的。在一些情況下，我們希望對於某些特定的模塊，該item可見，而其他模塊不可見。

下面我們來看一個例子：

```Rust
// Intent: `a` exports `I`, `bar`, and `foo`, but nothing else.
pub mod a {
    pub const I: i32 = 3;

    // `semisecret` will be used "many" places within `a`, but
    // is not meant to be exposed outside of `a`.
    fn semisecret(x: i32) -> i32  { use self::b::c::J; x + J }

    pub fn bar(z: i32) -> i32 { semisecret(I) * z }
    pub fn foo(y: i32) -> i32 { semisecret(I) + y }

    mod b {
        mod c {
            const J: i32 = 4; // J is meant to be hidden from the outside world.
        }
    }
}
```

這段代碼編譯無法通過，因為 `J` 無法在 `mod c` 的外部訪問，而 `fn semisecret` 嘗試在 `mod a` 中訪問 `J`.

在 rust1.18 之前，保持`J`私有，並能夠讓 `a` 使用 `fn semisecret` 的正確寫法是，將 `fn semisecret` 移動到 `mod c` 中，並將其 `pub`，之後根據需要可以重新導出 `semisecret`。(如果不需要保持 `J` 的私有化，那麼可以對其進行 `pub`，之後可以在 `b` 中 `pub use self::c::J` 或者直接 `pub c`)

```Rust
// Intent: `a` exports `I`, `bar`, and `foo`, but nothing else.
pub mod a {
    pub const I: i32 = 3;

    // `semisecret` will be used "many" places within `a`, but
    // is not meant to be exposed outside of `a`.
    // (If we put `pub use` here, then *anyone* could access it.)
    use self::b::semisecret;

    pub fn bar(z: i32) -> i32 { semisecret(I) * z }
    pub fn foo(y: i32) -> i32 { semisecret(I) + y }

    mod b {
        pub use self::c::semisecret;
        mod c {
            const J: i32 = 4; // J is meant to be hidden from the outside world.
            pub fn semisecret(x: i32) -> i32  { x + J }
        }
    }
}
```

這種情況可以正常工作，但是，這裡有個嚴重的問題：沒有人能夠十分清晰的說明 `pub fn semisecret` 使用到了哪些地方，需要通過上下文進行判斷：

1. 所有可以訪問 `semisecret` 的模塊；
2. 在所有可以訪問 `semisecret` 的模塊中，是否存在 `semisecret` 的 re-export;

同時，如果在 `a` 中使用 `pub use self::b::semisecret` ，那麼所有人都可以通過 `use` 訪問 `fn semisecret`，但是實際上，這個函數只需要讓 `mod a` 訪問就可以了。

## pub restricted 的使用

### Syntax

old:

    VISIBILITY ::= <empty> | `pub`

new:

    VISIBILITY ::= <empty> | `pub` | `pub` `(` USE_PATH `)` | `pub` `(` `crate` `)`

pub\(restriction\) 意味著對 item，method，field等的定義加以可見範圍（作用域）的限制。

可見範圍（作用域）分為所有 crate \(無限制\)，當前 crate，當前 crate 中的子模塊的絕對路徑。被限制的東西不能在其限制範圍之外直接使用。

* `pub` 無明確指定意味著無限制；
* `pub(crate)` 當前 crate 有效；
* `pub(in <path>)` 在 `<path>` 表示的模塊中有效。

### 修改示例

```Rust
// Intent: `a` exports `I`, `bar`, and `foo`, but nothing else.
pub mod a {
    pub const I: i32 = 3;

    // `semisecret` will be used "many" places within `a`, but
    // is not meant to be exposed outside of `a`.
    // (`pub use` would be *rejected*; see Note 1 below)
    use self::b::semisecret;

    pub fn bar(z: i32) -> i32 { semisecret(I) * z }
    pub fn foo(y: i32) -> i32 { semisecret(I) + y }

    mod b {
        pub(in a) use self::c::semisecret;
        mod c {
            const J: i32 = 4; // J is meant to be hidden from the outside world.

            // `pub(in a)` means "usable within hierarchy of `mod a`, but not
            // elsewhere."
            pub(in a) fn semisecret(x: i32) -> i32  { x + J }
        }
    }
}
```

Note 1: 如果改成下面這種方式，編譯器會報錯:

```Rust
pub mod a { [...] pub use self::b::semisecret; [...] }
```

因為 `pub(in a) fn semisecret` 說明這個函數只能在 `a` 中使用，不允許 `pub` 出 `a` 的範圍。

### 限制字段示例

```Rust
mod a {
    #[derive(Default)]
    struct Priv(i32);

    pub mod b {
        use a::Priv as Priv_a;

        #[derive(Default)]
        pub struct F {
            pub    x: i32,
                   y: Priv_a,
            pub(in a) z: Priv_a,
        }

        #[derive(Default)]
        pub struct G(pub i32, Priv_a, pub(in a) Priv_a);

        // ... accesses to F.{x,y,z} ...
        // ... accesses to G.{0,1,2} ...
    }
    // ... accesses to F.{x,z} ...
    // ... accesses to G.{0,2} ...
}

mod k {
    use a::b::{F, G};
    // ... accesses to F and F.x ...
    // ... accesses to G and G.0 ...
}
```

### Crate 限制示例

Crate `c1`:

```Rust
pub mod a {
    struct Priv(i32);

    pub(crate) struct R { pub y: i32, z: Priv } // ok: field allowed to be more public
    pub        struct S { pub y: i32, z: Priv }

    pub fn to_r_bad(s: S) -> R { ... } //~ ERROR: `R` restricted solely to this crate

    pub(crate) fn to_r(s: S) -> R { R { y: s.y, z: s.z } } // ok: restricted to crate
}

use a::{R, S}; // ok: `a::R` and `a::S` are both visible

pub use a::R as ReexportAttempt; //~ ERROR: `a::R` restricted solely to this crate
```

Crate `c2`:

```Rust
extern crate c1;

use c1::a::S; // ok: `S` is unrestricted

use c1::a::R; //~ ERROR: `c1::a::R` not visible outside of its crate
```
