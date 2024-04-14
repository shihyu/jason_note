```rust
use reqwest;
use std::error::Error;
use std::{fs::File, io::copy};
use tokio;

async fn async_call() -> Result<(), Box<dyn Error>> {
    // 下载图片
    let response = reqwest::get("https://upload.wikimedia.org/wikipedia/zh/3/34/Lenna.jpg").await?;

    // 确认请求是否成功
    if response.status().is_success() {
        // 读取响应内容
        let bytes = response.bytes().await?;

        // 将图像内容写入文件
        std::fs::write("image_async.jpg", bytes)?;

        println!("异步图片下载成功！");
    } else {
        println!("Error: {}", response.status());
    }

    Ok(())
}

fn sync_call() -> Result<(), Box<dyn std::error::Error>> {
    // 发起GET请求
    let response =
        reqwest::blocking::get("https://upload.wikimedia.org/wikipedia/zh/3/34/Lenna.jpg")?;

    // 检查请求是否成功
    if !response.status().is_success() {
        panic!("请求失败: {}", response.status());
    }

    let mut file = File::create("Lenna.jpg")?;
    copy(&mut response.bytes().unwrap().as_ref(), &mut file)?;

    println!("图片已下载到Lenna.jpg");

    Ok(())
}


fn main() {
    // 调用同步函数
    if let Err(err) = sync_call() {
        eprintln!("同步任务出错: {:?}", err);
    }

    let rt = tokio::runtime::Runtime::new().unwrap();
    // 在 tokio 运行时内部执行异步任务
    rt.block_on(async {
        // 调用异步函数
        if let Err(err) = async_call().await {
            eprintln!("异步任务出错: {:?}", err);
        }
    });
}

```

