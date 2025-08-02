use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::Duration;
use std::collections::HashMap;

// Actor 模式實現
#[derive(Debug)]
enum Message {
    Set { key: String, value: String },
    Get { key: String, response: mpsc::Sender<Option<String>> },
    Delete { key: String },
    Stop,
}

// Key-Value Actor
struct KeyValueActor {
    receiver: mpsc::Receiver<Message>,
    data: HashMap<String, String>,
}

impl KeyValueActor {
    fn new() -> (mpsc::Sender<Message>, thread::JoinHandle<()>) {
        let (sender, receiver) = mpsc::channel();
        
        let handle = thread::spawn(move || {
            let mut actor = KeyValueActor {
                receiver,
                data: HashMap::new(),
            };
            actor.run();
        });
        
        (sender, handle)
    }
    
    fn run(&mut self) {
        loop {
            match self.receiver.recv() {
                Ok(Message::Set { key, value }) => {
                    println!("Actor: 設定 {} = {}", key, value);
                    self.data.insert(key, value);
                }
                Ok(Message::Get { key, response }) => {
                    let value = self.data.get(&key).cloned();
                    println!("Actor: 查詢 {} = {:?}", key, value);
                    let _ = response.send(value);
                }
                Ok(Message::Delete { key }) => {
                    let removed = self.data.remove(&key);
                    println!("Actor: 刪除 {} = {:?}", key, removed);
                }
                Ok(Message::Stop) => {
                    println!("Actor: 停止運行");
                    break;
                }
                Err(_) => {
                    println!("Actor: 發送端已關閉，退出");
                    break;
                }
            }
        }
    }
}

fn actor_pattern_example() {
    let (actor_sender, actor_handle) = KeyValueActor::new();
    
    // 多個客戶端執行緒
    let mut clients = vec![];
    
    for i in 0..3 {
        let sender = actor_sender.clone();
        let client = thread::spawn(move || {
            // 設定值
            sender.send(Message::Set {
                key: format!("key{}", i),
                value: format!("value{}", i),
            }).unwrap();
            
            // 查詢值
            let (response_tx, response_rx) = mpsc::channel();
            sender.send(Message::Get {
                key: format!("key{}", i),
                response: response_tx,
            }).unwrap();
            
            if let Ok(value) = response_rx.recv() {
                println!("客戶端 {} 收到回應: {:?}", i, value);
            }
            
            // 刪除值
            sender.send(Message::Delete {
                key: format!("key{}", i),
            }).unwrap();
        });
        clients.push(client);
    }
    
    // 等待所有客戶端完成
    for client in clients {
        client.join().unwrap();
    }
    
    // 停止 Actor
    actor_sender.send(Message::Stop).unwrap();
    actor_handle.join().unwrap();
}

// 執行緒池實現
type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: mpsc::Sender<Job>,
}

impl ThreadPool {
    pub fn new(size: usize) -> ThreadPool {
        assert!(size > 0);
        
        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));
        
        let mut workers = Vec::with_capacity(size);
        
        for id in 0..size {
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }
        
        ThreadPool { workers, sender }
    }
    
    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        self.sender.send(job).unwrap();
    }
}

impl Drop for ThreadPool {
    fn drop(&mut self) {
        println!("關閉所有工作者...");
        
        for worker in &mut self.workers {
            println!("關閉工作者 {}", worker.id);
            
            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            let job = receiver.lock().unwrap().recv();
            
            match job {
                Ok(job) => {
                    println!("工作者 {} 執行任務", id);
                    job();
                }
                Err(_) => {
                    println!("工作者 {} 斷開連接，關閉", id);
                    break;
                }
            }
        });
        
        Worker {
            id,
            thread: Some(thread),
        }
    }
}

fn thread_pool_example() {
    let pool = ThreadPool::new(4);
    
    for i in 0..8 {
        pool.execute(move || {
            println!("執行任務 {}", i);
            thread::sleep(Duration::from_secs(1));
            println!("任務 {} 完成", i);
        });
    }
    
    println!("所有任務已提交");
    thread::sleep(Duration::from_secs(3)); // 等待任務完成
}

// 效能監控包裝器
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Instant;

#[derive(Debug)]
struct LockMetrics {
    acquisitions: AtomicU64,
    contentions: AtomicU64,
    total_wait_time: AtomicU64,
    max_wait_time: AtomicU64,
}

impl LockMetrics {
    fn new() -> Self {
        LockMetrics {
            acquisitions: AtomicU64::new(0),
            contentions: AtomicU64::new(0),
            total_wait_time: AtomicU64::new(0),
            max_wait_time: AtomicU64::new(0),
        }
    }
    
    fn record_acquisition(&self, wait_time: Duration, contended: bool) {
        self.acquisitions.fetch_add(1, Ordering::Relaxed);
        
        if contended {
            self.contentions.fetch_add(1, Ordering::Relaxed);
        }
        
        let wait_nanos = wait_time.as_nanos() as u64;
        self.total_wait_time.fetch_add(wait_nanos, Ordering::Relaxed);
        
        // 更新最大等待時間
        let mut current_max = self.max_wait_time.load(Ordering::Relaxed);
        while wait_nanos > current_max {
            match self.max_wait_time.compare_exchange_weak(
                current_max,
                wait_nanos,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(x) => current_max = x,
            }
        }
    }
    
    fn report(&self) {
        let acquisitions = self.acquisitions.load(Ordering::Relaxed);
        let contentions = self.contentions.load(Ordering::Relaxed);
        let total_wait = self.total_wait_time.load(Ordering::Relaxed);
        let max_wait = self.max_wait_time.load(Ordering::Relaxed);
        
        if acquisitions > 0 {
            let contention_rate = (contentions as f64 / acquisitions as f64) * 100.0;
            let avg_wait = total_wait as f64 / acquisitions as f64;
            
            println!("🔒 鎖統計報告:");
            println!("  總獲取次數: {}", acquisitions);
            println!("  競爭次數: {}", contentions);
            println!("  競爭率: {:.2}%", contention_rate);
            println!("  平均等待時間: {:.2}ns", avg_wait);
            println!("  最大等待時間: {}ns", max_wait);
        }
    }
}

// 監控包裝器
struct MonitoredMutex<T> {
    inner: Mutex<T>,
    metrics: LockMetrics,
}

impl<T> MonitoredMutex<T> {
    fn new(data: T) -> Self {
        MonitoredMutex {
            inner: Mutex::new(data),
            metrics: LockMetrics::new(),
        }
    }
    
    fn lock(&self) -> std::sync::MutexGuard<T> {
        let start = Instant::now();
        let guard = self.inner.lock().unwrap();
        let wait_time = start.elapsed();
        
        // 判斷是否有競爭 (簡單的啟發式方法)
        let contended = wait_time > Duration::from_nanos(1000);
        self.metrics.record_acquisition(wait_time, contended);
        
        guard
    }
    
    fn metrics(&self) -> &LockMetrics {
        &self.metrics
    }
}

fn performance_monitoring_example() {
    let counter = Arc::new(MonitoredMutex::new(0));
    let mut handles = vec![];
    
    // 建立多個競爭執行緒
    for i in 0..4 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for j in 0..1000 {
                {
                    let mut guard = counter.lock();
                    *guard += 1;
                    
                    // 模擬一些工作
                    if j % 100 == 0 {
                        thread::sleep(Duration::from_micros(10));
                    }
                }
                
                // 偶爾讓出CPU
                if j % 50 == 0 {
                    thread::yield_now();
                }
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("最終計數: {}", *counter.lock());
    println!("\n最終統計:");
    counter.metrics().report();
}

fn main() {
    println!("=== Actor Pattern Example ===");
    actor_pattern_example();
    
    println!("\n=== Thread Pool Example ===");
    thread_pool_example();
    
    println!("\n=== Performance Monitoring Example ===");
    performance_monitoring_example();
}