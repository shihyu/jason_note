// Compare-and-Swap 操作 - 高級原子操作
// 演示 CAS 操作的強大功能和應用場景

use std::sync::atomic::{AtomicI32, AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

fn main() {
    println!("🔄 Compare-and-Swap 操作範例");
    println!("=============================");
    
    basic_cas_demo();
    println!("\n{}", "=".repeat(40));
    lock_free_stack_demo();
    println!("\n{}", "=".repeat(40));
    retry_mechanism_demo();
}

fn basic_cas_demo() {
    println!("🎯 基本 CAS 操作示範:");
    
    let value = Arc::new(AtomicI32::new(10));
    let mut handles = vec![];
    
    // 啟動多個執行緒，每個都嘗試將值翻倍
    for i in 0..3 {
        let value = Arc::clone(&value);
        let handle = thread::spawn(move || {
            loop {
                let current = value.load(Ordering::SeqCst);
                let new_value = current * 2;
                
                // 嘗試 CAS 操作：只有當值仍然是 current 時才更新為 new_value
                match value.compare_exchange_weak(
                    current, 
                    new_value, 
                    Ordering::SeqCst, 
                    Ordering::SeqCst
                ) {
                    Ok(_) => {
                        println!("✅ 執行緒{}: 成功將 {} 更新為 {}", i, current, new_value);
                        break;
                    }
                    Err(actual) => {
                        println!("❌ 執行緒{}: CAS失敗，期望{}但實際是{}", i, current, actual);
                        // 繼續重試
                    }
                }
                thread::sleep(Duration::from_millis(10));
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("🎯 最終值: {}", value.load(Ordering::SeqCst));
}

fn lock_free_stack_demo() {
    println!("📚 無鎖堆疊示範 (簡化版):");
    
    // 使用原子指標模擬一個簡單的無鎖計數器
    let counter = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];
    
    // 多個執行緒並發地添加項目
    for i in 0..4 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for j in 0..5 {
                loop {
                    let current = counter.load(Ordering::SeqCst);
                    let new_value = current + 1;
                    
                    if counter.compare_exchange_weak(
                        current,
                        new_value,
                        Ordering::SeqCst,
                        Ordering::SeqCst
                    ).is_ok() {
                        println!("📦 執行緒{}: 成功添加項目{} (總計: {})", i, j, new_value);
                        break;
                    }
                    // CAS 失敗，重試
                    thread::yield_now();
                }
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("🎯 堆疊中總項目數: {}", counter.load(Ordering::SeqCst));
    println!("💡 無鎖資料結構避免了鎖競爭，但需要小心設計");
}

fn retry_mechanism_demo() {
    println!("🔁 重試機制示範:");
    
    let shared_resource = Arc::new(AtomicI32::new(100));
    let mut handles = vec![];
    
    // 模擬多個執行緒嘗試"購買"資源
    for i in 0..5 {
        let resource = Arc::clone(&shared_resource);
        let handle = thread::spawn(move || {
            let cost = 20 + i * 5; // 每個執行緒需要不同數量的資源
            let mut attempts = 0;
            
            loop {
                let current = resource.load(Ordering::SeqCst);
                attempts += 1;
                
                if current < cost {
                    println!("💸 執行緒{}: 資源不足({} < {})，嘗試{}", i, current, cost, attempts);
                    thread::sleep(Duration::from_millis(100));
                    if attempts > 10 {
                        println!("⏰ 執行緒{}: 超時退出", i);
                        break;
                    }
                    continue;
                }
                
                let new_value = current - cost;
                match resource.compare_exchange_weak(
                    current,
                    new_value,
                    Ordering::SeqCst,
                    Ordering::SeqCst
                ) {
                    Ok(_) => {
                        println!("💰 執行緒{}: 成功購買! 花費{}，剩餘{} (嘗試{}次)", 
                                i, cost, new_value, attempts);
                        break;
                    }
                    Err(actual) => {
                        println!("🔄 執行緒{}: 重試中... 期望{}實際{}", i, current, actual);
                        thread::yield_now();
                    }
                }
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("🎯 最終剩餘資源: {}", shared_resource.load(Ordering::SeqCst));
    println!("💡 CAS操作是實現無鎖演算法的核心工具");
}