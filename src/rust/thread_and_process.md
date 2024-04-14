```rust
use std::process::Command;

fn print_data(data: Vec<i32>) {
    println!("Data: {:?}", data);
}

fn main() {
    let data = vec![1, 2, 3];

    // 啟動子進程，執行 print_data 函式
    let mut handle1 = Command::new("cargo")
        .args(&["run", "--bin", "print_data"]) // 假設 print_data 是您的另一個 Rust 程式
        .spawn()
        .expect("Failed to start child process");

    // 啟動子進程，執行 task_process 函式
    let mut handle2 = Command::new("cargo")
        .args(&["run", "--bin", "task_process"]) // 假設 task_process 是您的另一個 Rust 程式
        .spawn()
        .expect("Failed to start child process");

    // 主進程繼續執行其他任務
    for i in 1..=3 {
        println!("Hello from main! {}", i);
        std::thread::sleep(std::time::Duration::from_millis(1000));
    }

    // 等待子進程結束
    handle1.wait().expect("Failed to wait for child process");
    handle2.wait().expect("Failed to wait for child process");

}
```


```rust
use std::{
    process::{exit, Command},
    thread::sleep,
    time::Duration,
};

use nix::{
    sys::wait::waitpid,
    unistd::{fork, ForkResult},
};

fn main() {
    unsafe {
        match fork().expect("Failed to fork process") {
            ForkResult::Parent { child } => {
                println!("Try to kill me to check if the target process will be killed");

                // Do not forget to wait for the fork in order to prevent it from becoming a zombie!!!
                waitpid(Some(child), None).unwrap();

                // You have 120 seconds to kill the process :)
                sleep(Duration::from_secs(120));
            }

            ForkResult::Child => {
                // replace with your executable
                Command::new("/usr/bin/file-roller")
                    .spawn()
                    .expect("failed to spawn the target process");
                exit(0);
            }
        }
    }
}

```

```
[package]
name = "test_nix"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
nix = "0.22.0"
```
