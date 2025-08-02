// 原子旗標控制 - AtomicBool 範例
// 演示如何使用原子布林值控制執行緒行為

use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

fn main() {
    println!("🚩 原子旗標控制範例");
    println!("====================");
    
    thread_control_demo();
    println!("\n{}", "=".repeat(40));
    producer_consumer_flags();
}

fn thread_control_demo() {
    println!("🎛️  執行緒控制示範:");
    
    let running = Arc::new(AtomicBool::new(true));
    let counter = Arc::new(AtomicUsize::new(0));
    
    // 工作執行緒
    let running_clone = Arc::clone(&running);
    let counter_clone = Arc::clone(&counter);
    let worker = thread::spawn(move || {
        let mut local_count = 0;
        while running_clone.load(Ordering::SeqCst) {
            // 執行一些工作
            counter_clone.fetch_add(1, Ordering::SeqCst);
            local_count += 1;
            
            // 偶爾輸出進度
            if local_count % 50 == 0 {
                println!("🔄 工作執行緒已處理 {} 個項目", local_count);
            }
            
            thread::sleep(Duration::from_millis(10));
        }
        println!("✅ 工作執行緒優雅結束，總處理: {} 個項目", local_count);
    });
    
    // 監控執行緒
    let counter_monitor = Arc::clone(&counter);
    let running_monitor = Arc::clone(&running);
    let monitor = thread::spawn(move || {
        let mut last_count = 0;
        for second in 1..=3 {
            thread::sleep(Duration::from_secs(1));
            let current_count = counter_monitor.load(Ordering::SeqCst);
            let rate = current_count - last_count;
            println!("📊 第 {} 秒: 總計 {}, 速率 {}/秒", second, current_count, rate);
            last_count = current_count;
        }
        
        // 發送停止信號
        println!("🛑 發送停止信號");
        running_monitor.store(false, Ordering::SeqCst);
    });
    
    // 等待完成
    monitor.join().unwrap();
    worker.join().unwrap();
    
    println!("🎯 最終計數: {}", counter.load(Ordering::SeqCst));
}

fn producer_consumer_flags() {
    println!("🏭 生產者-消費者旗標示範:");
    
    let data_ready = Arc::new(AtomicBool::new(false));
    let data_value = Arc::new(AtomicUsize::new(0));
    let stop_flag = Arc::new(AtomicBool::new(false));
    
    // 生產者
    let data_ready_producer = Arc::clone(&data_ready);
    let data_value_producer = Arc::clone(&data_value);
    let stop_flag_producer = Arc::clone(&stop_flag);
    
    let producer = thread::spawn(move || {
        for i in 1..=5 {
            // 準備資料
            thread::sleep(Duration::from_millis(500));
            data_value_producer.store(i * 10, Ordering::SeqCst);
            
            // 設定資料準備旗標
            data_ready_producer.store(true, Ordering::SeqCst);
            println!("📦 生產者: 資料 {} 已準備", i * 10);
            
            // 等待消費者處理
            while data_ready_producer.load(Ordering::SeqCst) {
                thread::sleep(Duration::from_millis(10));
            }
        }
        
        // 發送停止信號
        stop_flag_producer.store(true, Ordering::SeqCst);
        println!("🏁 生產者: 所有資料已生產完畢");
    });
    
    // 消費者
    let data_ready_consumer = Arc::clone(&data_ready);
    let data_value_consumer = Arc::clone(&data_value);
    let stop_flag_consumer = Arc::clone(&stop_flag);
    
    let consumer = thread::spawn(move || {
        let mut processed = 0;
        loop {
            // 檢查是否有資料準備好
            if data_ready_consumer.load(Ordering::SeqCst) {
                let value = data_value_consumer.load(Ordering::SeqCst);
                println!("📥 消費者: 處理資料 {}", value);
                
                // 模擬處理時間
                thread::sleep(Duration::from_millis(200));
                processed += 1;
                
                // 標記資料已處理
                data_ready_consumer.store(false, Ordering::SeqCst);
            }
            
            // 檢查停止信號
            if stop_flag_consumer.load(Ordering::SeqCst) {
                break;
            }
            
            thread::sleep(Duration::from_millis(50));
        }
        println!("✅ 消費者: 完成，總處理 {} 個項目", processed);
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
    
    println!("💡 提示：原子旗標是實現簡單協調機制的理想選擇");
}