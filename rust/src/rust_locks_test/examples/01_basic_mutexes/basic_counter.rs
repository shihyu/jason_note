// 基本計數器 - Arc<Mutex<T>> 範例
// 演示多執行緒共享和修改整數計數器

use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    println!("🔒 基本 Arc<Mutex<T>> 計數器範例");
    println!("=====================================");
    
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    // 建立 5 個執行緒，每個執行緒增加計數器 1000 次
    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                let mut num = counter.lock().unwrap();
                *num += 1;
            }
            println!("✅ 執行緒 {} 完成", i);
        });
        handles.push(handle);
    }

    // 等待所有執行緒完成
    for handle in handles {
        handle.join().unwrap();
    }

    println!("🎯 最終計數: {}", *counter.lock().unwrap());
    println!("   預期結果: 5000");
}