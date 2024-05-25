## Rust 使用 reqwest 發送 HTTP 請求

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

---

## Blocking implementation

First let’s add the following dependencies using `cargo add`:

```bash
# Add anyhow as a dependency
cargo add anyhow
# Add reqwest with blocking feature
cargo add reqwest -F blocking
```

```rust
use std::{fs::File, io::copy};
use anyhow::Result;

fn download_image_to(url: &str, file_name: &str) -> Result<()> {
    // Send an HTTP GET request to the URL
    let mut response = reqwest::blocking::get(url)?;

    // Create a new file to write the downloaded image to
    let mut file = File::create(file_name)?;

    // Copy the contents of the response to the file
    copy(&mut response, &mut file)?;

    Ok(())
}

fn main() {
    let image_url = "https://www.rust-lang.org/static/images/rust-logo-blk.svg";
    let file_name = "rust-logo-blk.svg";
    match download_image_to(image_url, file_name) {
        Ok(_) => println!("image saved successfully"),
        Err(e) => println!("error while downloading image: {}", e),
    }
}
```

## Non-blocking (async) implementation

In contrast to the first iteration, we can use `tokio` and leverage non-blocking APIs provided by `reqwest` to solve the trivia by applying asynchronous programming techniques. First, let’s add the necessary dependencies:

```bash
# Add anyhow as a dependency
cargo add anyhow
# Add reqwest with blocking feature
cargo add reqwest -F blocking
# Add tokio with full featureset
cargo add tokio -F full
```

Having the crates added to our project, we can move on and implement downloading and storing the image from an URL:

```rust
use std::{fs::File, io::{copy, Cursor}};
use anyhow::Result;

async fn download_image_to(url: &str, file_name: &str) -> Result<()> {
    // Send an HTTP GET request to the URL
    let response = reqwest::get(url).await?;
    // Create a new file to write the downloaded image to
    let mut file = File::create(file_name)?;
    
    // Create a cursor that wraps the response body
    let mut content =  Cursor::new(response.bytes().await?);
    // Copy the content from the cursor to the file
    copy(&mut content, &mut file)?;

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    let image_url = "https://www.rust-lang.org/static/images/rust-logo-blk.svg";
    let file_name = "rust-logo-blk.svg";
    match download_image_to(image_url, file_name).await {
        Ok(_) => println!("image saved successfully"),
        Err(e) => println!("error while downloading image: {}", e),
    }
    Ok(())
}
```
