use std::sync::atomic::{AtomicI32, AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

fn basic_atomic_example() {
    let counter = Arc::new(AtomicI32::new(0));
    let mut handles = vec![];
    
    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                counter.fetch_add(1, Ordering::SeqCst);
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("最終計數: {}", counter.load(Ordering::SeqCst));
}

fn atomic_flag_example() {
    let running = Arc::new(AtomicBool::new(true));
    let counter = Arc::new(AtomicUsize::new(0));
    
    // 工作執行緒
    let running_clone = Arc::clone(&running);
    let counter_clone = Arc::clone(&counter);
    let worker = thread::spawn(move || {
        while running_clone.load(Ordering::SeqCst) {
            counter_clone.fetch_add(1, Ordering::SeqCst);
            thread::sleep(Duration::from_millis(10));
        }
        println!("工作執行緒結束");
    });
    
    // 主執行緒等待3秒後停止
    thread::sleep(Duration::from_secs(3));
    running.store(false, Ordering::SeqCst);
    
    worker.join().unwrap();
    println!("總計數: {}", counter.load(Ordering::SeqCst));
}

fn cas_example() {
    let value = Arc::new(AtomicI32::new(10));
    let mut handles = vec![];
    
    for i in 0..3 {
        let value = Arc::clone(&value);
        let handle = thread::spawn(move || {
            loop {
                let current = value.load(Ordering::SeqCst);
                let new_value = current * 2;
                
                match value.compare_exchange_weak(
                    current, 
                    new_value, 
                    Ordering::SeqCst, 
                    Ordering::SeqCst
                ) {
                    Ok(_) => {
                        println!("執行緒 {} 成功將 {} 更新為 {}", i, current, new_value);
                        break;
                    }
                    Err(actual) => {
                        println!("執行緒 {} CAS 失敗，期望 {} 但實際是 {}", i, current, actual);
                    }
                }
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("最終值: {}", value.load(Ordering::SeqCst));
}

fn memory_ordering_example() {
    let data = Arc::new(AtomicI32::new(0));
    let flag = Arc::new(AtomicBool::new(false));
    
    // 生產者執行緒
    let data_producer = Arc::clone(&data);
    let flag_producer = Arc::clone(&flag);
    let producer = thread::spawn(move || {
        // 1. 寫入資料
        data_producer.store(42, Ordering::Relaxed);
        
        // 2. 設定旗標 (Release語義)
        flag_producer.store(true, Ordering::Release);
        
        println!("生產者：資料寫入完成");
    });
    
    // 消費者執行緒
    let data_consumer = Arc::clone(&data);
    let flag_consumer = Arc::clone(&flag);
    let consumer = thread::spawn(move || {
        // 等待旗標 (Acquire語義)
        while !flag_consumer.load(Ordering::Acquire) {
            thread::sleep(Duration::from_millis(1));
        }
        
        let value = data_consumer.load(Ordering::Relaxed);
        println!("消費者：讀取到資料 {}", value);
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
}

fn ordering_performance_test() {
    let counter = Arc::new(AtomicI32::new(0));
    let iterations = 1_000_000;
    
    // 測試 SeqCst (最強順序)
    let start = Instant::now();
    let counter_seqcst = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        for _ in 0..iterations {
            counter_seqcst.fetch_add(1, Ordering::SeqCst);
        }
    });
    handle.join().unwrap();
    let seqcst_time = start.elapsed();
    
    counter.store(0, Ordering::SeqCst);
    
    // 測試 Relaxed (最弱順序)
    let start = Instant::now();
    let counter_relaxed = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        for _ in 0..iterations {
            counter_relaxed.fetch_add(1, Ordering::Relaxed);
        }
    });
    handle.join().unwrap();
    let relaxed_time = start.elapsed();
    
    println!("SeqCst 時間: {:?}", seqcst_time);
    println!("Relaxed 時間: {:?}", relaxed_time);
    println!("Relaxed 比 SeqCst 快 {:.2}x", 
        seqcst_time.as_nanos() as f64 / relaxed_time.as_nanos() as f64);
}

fn main() {
    println!("=== Basic Atomic Example ===");
    basic_atomic_example();
    
    println!("\n=== Atomic Flag Example ===");
    atomic_flag_example();
    
    println!("\n=== Compare-And-Swap Example ===");
    cas_example();
    
    println!("\n=== Memory Ordering Example ===");
    memory_ordering_example();
    
    println!("\n=== Performance Test ===");
    ordering_performance_test();
}