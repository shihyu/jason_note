
定義枚舉，並使用match表達式來匹配枚舉值。
在match表達式中，使用枚舉成員作為分支條件，並在每個分支中編寫相應的代碼邏輯。

示例代碼：

```shell
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
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

fn main() {
    println!("{}", value_in_cents(Coin::Dime));
}
```