
如果沒有 if let 的話，用match只匹配一個模式的值的話，代碼有點繁瑣。

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => {
            1
        },
        _ => (2),
    }
}

fn main() {
    println!("{}", value_in_cents(Coin::Dime));
}
```

使用 if let 的話，代碼更加簡潔。 可以認為 if let 是 match 的一個語法糖，它當值匹配某一模式時執行代碼而忽略所有其他值。

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn main() {
    let a = Coin::Dime;
    if let a = Coin::Dime {
        println!("Dime");
    }
}   
```