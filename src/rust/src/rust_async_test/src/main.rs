use tokio::time::{sleep, Duration};

// 异步函数
async fn async_function(id: usize) {
    println!("Start of async function {}", id);

    // 模拟异步操作，例如 I/O 操作
    sleep(Duration::from_secs(2)).await;

    println!("End of async function {}", id);
}

// 您可以一次連續呼叫 async_function 多次。在非同步程式設計中，您可以使用 tokio::spawn 或其他類似的功能來並行執行多個非同步任務。下面是一個例子，演示如何連續呼叫 async_function 5 次
#[tokio::main]
async fn main() {
    println!("Start of main function");

    // 创建一个 Vec 来存储任务句柄
    let mut handles = Vec::new();

    // 调用 async_function 5 次
    for i in 0..5 {
        // 使用 tokio::spawn 启动异步任务，并将任务句柄存储在 Vec 中
        let handle = tokio::spawn(async_function(i));
        handles.push(handle);
    }

    // 等待所有任务完成
    for handle in handles {
        handle.await.expect("Failed to await task");
    }

    println!("End of main function");
}
