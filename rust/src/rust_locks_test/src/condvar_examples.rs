use std::sync::{Arc, Mutex, Condvar};
use std::thread;
use std::time::Duration;
use std::collections::VecDeque;

struct ProducerConsumer<T> {
    buffer: Mutex<VecDeque<T>>,
    not_empty: Condvar,
    not_full: Condvar,
    capacity: usize,
}

impl<T> ProducerConsumer<T> {
    fn new(capacity: usize) -> Self {
        ProducerConsumer {
            buffer: Mutex::new(VecDeque::new()),
            not_empty: Condvar::new(),
            not_full: Condvar::new(),
            capacity,
        }
    }
    
    fn produce(&self, item: T) {
        let mut buffer = self.buffer.lock().unwrap();
        
        // 等待緩衝區有空間
        while buffer.len() >= self.capacity {
            println!("緩衝區滿了，生產者等待...");
            buffer = self.not_full.wait(buffer).unwrap();
        }
        
        buffer.push_back(item);
        println!("生產了一個項目，緩衝區大小: {}", buffer.len());
        
        // 通知消費者
        self.not_empty.notify_one();
    }
    
    fn consume(&self) -> T {
        let mut buffer = self.buffer.lock().unwrap();
        
        // 等待緩衝區有資料
        while buffer.is_empty() {
            println!("緩衝區空了，消費者等待...");
            buffer = self.not_empty.wait(buffer).unwrap();
        }
        
        let item = buffer.pop_front().unwrap();
        println!("消費了一個項目，緩衝區大小: {}", buffer.len());
        
        // 通知生產者
        self.not_full.notify_one();
        
        item
    }
}

fn producer_consumer_example() {
    let pc = Arc::new(ProducerConsumer::new(3)); // 緩衝區大小為3
    
    // 生產者執行緒
    let pc_producer = Arc::clone(&pc);
    let producer = thread::spawn(move || {
        for i in 0..10 {
            let item = format!("項目-{}", i);
            pc_producer.produce(item);
            thread::sleep(Duration::from_millis(100));
        }
        println!("生產者完成");
    });
    
    // 消費者執行緒
    let pc_consumer = Arc::clone(&pc);
    let consumer = thread::spawn(move || {
        for _ in 0..10 {
            let item = pc_consumer.consume();
            println!("收到: {}", item);
            thread::sleep(Duration::from_millis(200)); // 消費比生產慢
        }
        println!("消費者完成");
    });
    
    producer.join().unwrap();
    consumer.join().unwrap();
}

struct TaskCoordinator {
    workers_ready: Mutex<usize>,
    all_ready: Condvar,
    target_count: usize,
}

impl TaskCoordinator {
    fn new(target_count: usize) -> Self {
        TaskCoordinator {
            workers_ready: Mutex::new(0),
            all_ready: Condvar::new(),
            target_count,
        }
    }
    
    fn worker_ready(&self, worker_id: usize) {
        let mut count = self.workers_ready.lock().unwrap();
        *count += 1;
        
        println!("工作者 {} 準備就緒 ({}/{})", worker_id, *count, self.target_count);
        
        if *count >= self.target_count {
            println!("所有工作者準備就緒，開始任務！");
            self.all_ready.notify_all();
        } else {
            // 等待其他工作者
            while *count < self.target_count {
                println!("工作者 {} 等待其他工作者...", worker_id);
                count = self.all_ready.wait(count).unwrap();
            }
        }
    }
}

fn task_coordination_example() {
    let coordinator = Arc::new(TaskCoordinator::new(3));
    let mut handles = vec![];
    
    for i in 0..3usize {
        let coordinator = Arc::clone(&coordinator);
        let handle = thread::spawn(move || {
            // 模擬準備時間
            thread::sleep(Duration::from_millis(((i + 1) * 500) as u64));
            
            // 報告準備就緒並等待開始信號
            coordinator.worker_ready(i);
            
            // 開始執行任務
            println!("工作者 {} 開始執行任務", i);
            thread::sleep(Duration::from_secs(2));
            println!("工作者 {} 完成任務", i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

fn timeout_example() {
    let pair = Arc::new((Mutex::new(false), Condvar::new()));
    let pair_clone = Arc::clone(&pair);
    
    // 等待執行緒
    let waiter = thread::spawn(move || {
        let (lock, cvar) = &*pair_clone;
        let started = lock.lock().unwrap();
        
        // 等待條件滿足，最多等待2秒
        let result = cvar.wait_timeout_while(
            started,
            Duration::from_secs(2),
            |&mut pending| !pending,
        ).unwrap();
        
        if result.1.timed_out() {
            println!("等待超時！");
        } else {
            println!("條件滿足！");
        }
    });
    
    // 主執行緒等待3秒後設定條件
    thread::sleep(Duration::from_secs(3));
    
    let (lock, cvar) = &*pair;
    let mut started = lock.lock().unwrap();
    *started = true;
    cvar.notify_one();
    
    waiter.join().unwrap();
}

fn main() {
    println!("=== Producer-Consumer Example ===");
    producer_consumer_example();
    
    println!("\n=== Task Coordination Example ===");
    task_coordination_example();
    
    println!("\n=== Timeout Example ===");
    timeout_example();
}