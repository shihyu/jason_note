## Rust 使用 reqwest 发送 HTTP 请求

```rust
use reqwest;
use std::error::Error;
use std::{fs::File, io::copy};
use tokio;

async fn async_call() -> Result<(), Box<dyn Error>> {
    let response = reqwest::get("https://upload.wikimedia.org/wikipedia/zh/3/34/Lenna.jpg").await?;

    if response.status().is_success() {
        let bytes = response.bytes().await?;

        std::fs::write("image_async.jpg", bytes)?;

        println!("async download Lenna.jpg");
    } else {
        println!("Error: {}", response.status());
    }

    Ok(())
}

fn sync_call() -> Result<(), Box<dyn std::error::Error>> {
    let response =
        reqwest::blocking::get("https://upload.wikimedia.org/wikipedia/zh/3/34/Lenna.jpg")?;

    if !response.status().is_success() {
        panic!("response status: {}", response.status());
    }

    let mut file = File::create("Lenna.jpg")?;
    copy(&mut response.bytes().unwrap().as_ref(), &mut file)?;

    println!("sync download Lenna.jpg");

    Ok(())
}


fn main() {
    if let Err(err) = sync_call() {
        eprintln!("sync_call error: {:?}", err);
    }

    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        if let Err(err) = async_call().await {
            eprintln!("async_call error: {:?}", err);
        }
    });
}
```

```toml
[package]
name = "test_reqwest"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
reqwest = { version = "0.12.3", features = ["blocking"] }
tokio = { version = "1.37.0", features = ["full"] }
```

