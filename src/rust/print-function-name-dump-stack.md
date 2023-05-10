## print-function-name-dump-stack

```
cargo new print-function-name-dump-stack
```

- Cargo.toml

```toml
[package]
name = "print-function-name-dump-stack"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
stdext = "0.3.1"
backtrace = "0.3.65"
```

- main.rs

```rust
use backtrace::Backtrace;
use std::process;
use std::thread;
use stdext::function_name;

macro_rules! print_current_info {
    () => {{
        println!(
            "pid={},tid={:?} {}:{} {}",
            process::id(),
            thread::current().id(),
            file!(),
            line!(),
            function_name!()
        );
    }};
}

fn dump_stack_test() {
    let bt = Backtrace::new();
    print_current_info!();
    println!("backtrace dump start ===============");
    println!("{:?}", bt);
}

fn test_func() {
    print_current_info!();
    dump_stack_test();
}

fn main() {
    print_current_info!();
    test_func();
}
```
