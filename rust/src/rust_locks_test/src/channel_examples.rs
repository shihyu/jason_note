use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};
use crossbeam::channel;

fn basic_channel_example() {
    let (tx, rx) = mpsc::channel();
    
    // 發送者執行緒
    let tx_clone = tx.clone();
    thread::spawn(move || {
        for i in 0..5 {
            let message = format!("訊息 {}", i);
            tx_clone.send(message).unwrap();
            println!("發送: 訊息 {}", i);
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // 另一個發送者
    thread::spawn(move || {
        for i in 5..10 {
            let message = format!("訊息 {}", i);
            tx.send(message).unwrap();
            println!("發送: 訊息 {}", i);
            thread::sleep(Duration::from_millis(150));
        }
    });
    
    // 接收者
    for _ in 0..10 {
        let received = rx.recv().unwrap();
        println!("接收: {}", received);
    }
}

fn sync_channel_example() {
    // 建立同步通道，緩衝區大小為2
    let (tx, rx) = mpsc::sync_channel(2);
    
    let sender = thread::spawn(move || {
        for i in 0..5 {
            println!("準備發送 {}", i);
            match tx.send(i) {
                Ok(_) => println!("成功發送 {}", i),
                Err(e) => println!("發送失敗: {}", e),
            }
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // 接收者故意延遲
    thread::sleep(Duration::from_millis(500));
    
    for received in rx {
        println!("接收: {}", received);
        thread::sleep(Duration::from_millis(200));
    }
    
    sender.join().unwrap();
}

fn work_distribution_example() {
    let (job_tx, job_rx) = mpsc::channel();
    let (result_tx, result_rx) = mpsc::channel();
    
    // 將 receiver 包裝在 Arc<Mutex<>> 中以便共享
    let job_rx = Arc::new(Mutex::new(job_rx));
    
    // 工作者執行緒池
    let mut workers = vec![];
    for worker_id in 0..3 {
        let job_rx = Arc::clone(&job_rx);
        let result_tx = result_tx.clone();
        
        let worker = thread::spawn(move || {
            loop {
                let job_result = {
                    let rx = job_rx.lock().unwrap();
                    rx.recv()
                };
                
                match job_result {
                    Ok(job) => {
                        println!("工作者 {} 處理任務: {}", worker_id, job);
                        thread::sleep(Duration::from_millis(500));
                        let result = format!("任務 {} 的結果", job);
                        result_tx.send((worker_id, result)).unwrap();
                    }
                    Err(_) => {
                        println!("工作者 {} 結束", worker_id);
                        break;
                    }
                }
            }
        });
        workers.push(worker);
    }
    
    // 任務分發者
    let job_distributor = thread::spawn(move || {
        for i in 0..10 {
            job_tx.send(i).unwrap();
        }
        drop(job_tx); // 關閉通道
    });
    
    // 結果收集者
    let result_collector = thread::spawn(move || {
        let mut results = vec![];
        for (worker_id, result) in result_rx {
            println!("收到來自工作者 {} 的結果: {}", worker_id, result);
            results.push(result);
            if results.len() == 10 {
                break;
            }
        }
        results
    });
    
    job_distributor.join().unwrap();
    let results = result_collector.join().unwrap();
    
    for worker in workers {
        worker.join().unwrap();
    }
    
    println!("所有結果: {:?}", results);
}

fn crossbeam_channel_example() {
    let (tx, rx) = channel::unbounded();
    let (bounded_tx, bounded_rx) = channel::bounded(10);
    
    // 多個生產者
    let mut producers = vec![];
    for i in 0..3 {
        let tx = tx.clone();
        let producer = thread::spawn(move || {
            for j in 0..5 {
                let message = format!("生產者 {} 的訊息 {}", i, j);
                tx.send(message).unwrap();
                thread::sleep(Duration::from_millis(50));
            }
        });
        producers.push(producer);
    }
    
    // 使用 select! 處理多個通道
    let selector = thread::spawn(move || {
        loop {
            crossbeam::select! {
                recv(rx) -> msg => {
                    match msg {
                        Ok(message) => println!("從無界通道收到: {}", message),
                        Err(_) => break,
                    }
                },
                recv(bounded_rx) -> msg => {
                    match msg {
                        Ok(message) => println!("從有界通道收到: {}", message),
                        Err(_) => {},
                    }
                },
                default(Duration::from_millis(100)) => {
                    println!("等待訊息超時...");
                },
            }
        }
    });
    
    // 向有界通道發送訊息
    thread::spawn(move || {
        for i in 0..3 {
            bounded_tx.send(format!("有界訊息 {}", i)).unwrap();
            thread::sleep(Duration::from_millis(200));
        }
    });
    
    for producer in producers {
        producer.join().unwrap();
    }
    
    drop(tx);
    selector.join().unwrap();
}

fn channel_performance_test() {
    let message_count = 1_000_000;
    
    // 標準庫 channel
    let start = Instant::now();
    let (tx, rx) = std::sync::mpsc::channel();
    
    let sender = thread::spawn(move || {
        for i in 0..message_count {
            tx.send(i).unwrap();
        }
    });
    
    let receiver = thread::spawn(move || {
        for _ in 0..message_count {
            rx.recv().unwrap();
        }
    });
    
    sender.join().unwrap();
    receiver.join().unwrap();
    let std_time = start.elapsed();
    
    // crossbeam channel
    let start = Instant::now();
    let (tx, rx) = channel::unbounded();
    
    let sender = thread::spawn(move || {
        for i in 0..message_count {
            tx.send(i).unwrap();
        }
    });
    
    let receiver = thread::spawn(move || {
        for _ in 0..message_count {
            rx.recv().unwrap();
        }
    });
    
    sender.join().unwrap();
    receiver.join().unwrap();
    let crossbeam_time = start.elapsed();
    
    println!("標準庫 channel: {:?}", std_time);
    println!("Crossbeam channel: {:?}", crossbeam_time);
    println!("效能比較: {:.2}x", 
        std_time.as_nanos() as f64 / crossbeam_time.as_nanos() as f64);
}

fn main() {
    println!("=== Basic Channel Example ===");
    basic_channel_example();
    
    println!("\n=== Sync Channel Example ===");
    sync_channel_example();
    
    println!("\n=== Work Distribution Example ===");
    work_distribution_example();
    
    println!("\n=== Crossbeam Channel Example ===");
    crossbeam_channel_example();
    
    println!("\n=== Channel Performance Test ===");
    channel_performance_test();
}