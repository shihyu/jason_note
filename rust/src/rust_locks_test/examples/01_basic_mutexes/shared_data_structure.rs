// 共享資料結構 - 複雜資料的多執行緒操作
// 演示如何在多執行緒環境中安全地修改結構體

use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

#[derive(Debug)]
struct SharedData {
    value: i32,
    items: Vec<String>,
}

impl SharedData {
    fn new() -> Self {
        SharedData {
            value: 0,
            items: Vec::new(),
        }
    }
    
    fn add_item(&mut self, item: String) {
        self.value += 1;
        self.items.push(item);
        println!("📝 新增項目: {}, 總計: {}", 
                 self.items.last().unwrap(), self.value);
    }
}

fn main() {
    println!("📊 共享資料結構範例");
    println!("=====================");
    
    let data = Arc::new(Mutex::new(SharedData::new()));
    let mut handles = vec![];

    // 建立 3 個執行緒，每個執行緒添加 3 個項目
    for i in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let item = format!("執行緒{}-項目{}", i, j);
                {
                    let mut shared = data.lock().unwrap();
                    shared.add_item(item);
                }
                thread::sleep(Duration::from_millis(100));
            }
            println!("✅ 執行緒 {} 完成", i);
        });
        handles.push(handle);
    }

    // 等待所有執行緒完成
    for handle in handles {
        handle.join().unwrap();
    }

    let final_data = data.lock().unwrap();
    println!("\n🎯 最終資料:");
    println!("   總數量: {}", final_data.value);
    println!("   項目列表: {:?}", final_data.items);
}