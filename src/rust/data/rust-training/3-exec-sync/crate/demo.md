
一個使用外部crate的例子如下
rand crate 提供了一個名為 Rng 的特性（trait）

```
//file:Cargo.toml
[dependencies]
rand = "0.8.3"
```

```shell
use rand::Rng;
fn main() {
    let secret_number = rand::thread_rng().gen_range(1..101);
    println!("{}", secret_number);
}
```

```
# cargo run
73
```