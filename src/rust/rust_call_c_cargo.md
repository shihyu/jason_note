# Rust call C/C++ for Cargo

我們來建立我們的第一個專案吧，請打開終端機輸入以下的指令：

```sh
cargo init rust-call-c-cargo
```

需要引入cc依賴

- Cargo.toml

```sh
[package]
name = "rust-call-c-cargo"
version = "0.1.0"
edition = "2021"
authors = ["Jason <yaoshihyu@gmail.com>"]

build = "build.rs"

[dependencies]
libc = "0.2"

[build-dependencies]
cc = "1.0"
```



- build.rs

```rust
extern crate cc;

fn main() {
    cc::Build::new().file("src/double.c").compile("libdouble.a");
}
```



- main.rs

```rust
extern crate libc;

extern "C" {
    fn double_input(input: libc::c_int) -> libc::c_int;
}

fn main() {
    let input = 4;
    let output = unsafe { double_input(input) };
    println!("{} * 2 = {}", input, output);
}
```



- double.c

```c
int double_input(int input) {
    return input * 2;
}
```



 我們現在試著輸入 `cargo run` 來執行看

```sh
cargo run


```



