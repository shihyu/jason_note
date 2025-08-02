// 基本原子計數器 - AtomicI32 範例
// 演示無鎖的高效能計數操作

use std::sync::atomic::{AtomicI32, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

fn main() {
    println!("⚛️  基本原子計數器範例");
    println!("======================");
    
    basic_atomic_demo();
    println!("\n{}", "=".repeat(40));
    performance_comparison();
}

fn basic_atomic_demo() {
    println!("🧮 原子操作示範:");
    
    let counter = Arc::new(AtomicI32::new(0));
    let mut handles = vec![];
    
    let start_time = Instant::now();
    
    // 建立 5 個執行緒，每個執行緒增加計數器 1000 次
    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                // 原子增加操作 - 無需鎖定
                counter.fetch_add(1, Ordering::SeqCst);
            }
            println!("✅ 執行緒 {} 完成", i);
        });
        handles.push(handle);
    }
    
    // 等待所有執行緒完成
    for handle in handles {
        handle.join().unwrap();
    }
    
    let elapsed = start_time.elapsed();
    let final_count = counter.load(Ordering::SeqCst);
    
    println!("🎯 最終計數: {}", final_count);
    println!("   預期結果: 5000");
    println!("⏱️  執行時間: {:?}", elapsed);
}

fn performance_comparison() {
    println!("🏎️  效能比較 (原子操作 vs Mutex):");
    
    use std::sync::Mutex;
    
    let iterations = 100_000;
    
    // 測試原子操作
    let atomic_counter = Arc::new(AtomicI32::new(0));
    let start = Instant::now();
    
    let atomic_handle = thread::spawn({
        let counter = Arc::clone(&atomic_counter);
        move || {
            for _ in 0..iterations {
                counter.fetch_add(1, Ordering::Relaxed);
            }
        }
    });
    
    atomic_handle.join().unwrap();
    let atomic_time = start.elapsed();
    
    // 測試 Mutex
    let mutex_counter = Arc::new(Mutex::new(0));
    let start = Instant::now();
    
    let mutex_handle = thread::spawn({
        let counter = Arc::clone(&mutex_counter);
        move || {
            for _ in 0..iterations {
                let mut guard = counter.lock().unwrap();
                *guard += 1;
            }
        }
    });
    
    mutex_handle.join().unwrap();
    let mutex_time = start.elapsed();
    
    println!("⚛️  原子操作時間: {:?}", atomic_time);
    println!("🔒 Mutex 時間: {:?}", mutex_time);
    
    if atomic_time < mutex_time {
        let speedup = mutex_time.as_nanos() as f64 / atomic_time.as_nanos() as f64;
        println!("🚀 原子操作比 Mutex 快 {:.2}x", speedup);
    } else {
        println!("📊 在這個測試中，效能差異不明顯");
    }
    
    println!("💡 提示：原子操作在簡單數值操作時通常更快，且無死鎖風險");
}