
首先在lib.rs中定義函數。
- 第一種是普通的定義方式
- 第二種是將函數放入模塊中

```shell
pub mod parent_module {
    pub mod child_module {
        pub fn public_function2() ->i32{
            return 1;
        }
    }
}

pub fn public_function1() ->i32{
    return 2;
}
```

再到main.rs中調用函數。注意對於函數的調用方式的區別。

```shell
mod lib;
fn main() {
    let ret1 = lib::public_function1();
    let ret2 = lib::parent_module::child_module::public_function2();
    println!("{}", ret1);
    println!("{}", ret2);
}
```

在上述的例子中
- src/main.rs 就是一個與包同名的二進制 crate 的 crate 根
- src/lib.rs 就是一個庫 crate 的 crate 根