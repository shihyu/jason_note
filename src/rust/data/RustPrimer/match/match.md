# match關鍵字
模式匹配，多出現在函數式編程語言之中，為其複雜的類型系統提供一個簡單輕鬆的解構能力。比如從enum等數據結構中取出數據等等，但是在書寫上，相對比較複雜。我們來看一個例子:

```rust
enum Direction {
    East,
    West,
    North,
    South,
}

fn main() {
    let dire = Direction::South;
    match dire {
        Direction::East => println!("East"),
        Direction::North | Direction::South => {
            println!("South or North");
        },
        _ => println!("West"),
    };
}
```

這是一個沒什麼實際意義的程序，但是能清楚的表達出match的用法。看到這裡，你肯定能想起一個常見的控制語句——`switch`。沒錯，match可以起到和switch相同的作用。不過有幾點需要注意：

1. match所羅列的匹配，必須窮舉出其所有可能。當然，你也可以用 **_** 這個符號來代表其餘的所有可能性情況，就類似於switch中的`default`語句。
2. match的每一個分支都必須是一個表達式，並且，除非一個分支一定會觸發panic，這些分支的所有表達式的最終返回值類型必須相同。

關於第二點，有的同學可能不明白。這麼說吧，你可以把match整體視為一個表達式，既然是一個表達式，那麼就一定能求得它的結果。因此，這個結果當然就可以被賦予一個變量咯。
看代碼：

```rust
enum Direction {
    East,
    West,
    North,
    South,
}

fn main() {
    // let d_panic = Direction::South;
    let d_west = Direction::West;
    let d_str = match d_west {
        Direction::East => "East",
        Direction::North | Direction::South => {
            panic!("South or North");
        },
        _ => "West",
    };

    println!("{}", d_str);
}
```

## 解構初窺

match還有一個非常重要的作用就是對現有的數據結構進行解構，輕易的可以拿出其中的數據部分來。
比如，以下是比較常見的例子：

```rust
enum Action {
    Say(String),
    MoveTo(i32, i32),
    ChangeColorRGB(u16, u16, u16),
}

fn main() {
    let action = Action::Say("Hello Rust".to_string());
    match action {
        Action::Say(s) => {
            println!("{}", s);
        },
        Action::MoveTo(x, y) => {
            println!("point from (0, 0) move to ({}, {})", x, y);
        },
        Action::ChangeColorRGB(r, g, _) => {
            println!("change color into '(r:{}, g:{}, b:0)', 'b' has been ignored",
                r, g,
            );
        }
    }
}
```

有人說了，從這來看也並不覺得match有多神奇啊！別急，請看下一小節——>[模式](pattern.md)
