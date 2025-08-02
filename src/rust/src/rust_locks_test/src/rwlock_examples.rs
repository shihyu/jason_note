use std::sync::{Arc, RwLock, Mutex};
use std::thread;
use std::time::Duration;
use std::collections::HashMap;

#[derive(Debug, Clone)]
struct Config {
    settings: HashMap<String, String>,
    version: u32,
}

impl Config {
    fn new() -> Self {
        let mut settings = HashMap::new();
        settings.insert("theme".to_string(), "dark".to_string());
        settings.insert("language".to_string(), "zh-TW".to_string());
        
        Config { settings, version: 1 }
    }
    
    fn get_setting(&self, key: &str) -> Option<String> {
        self.settings.get(key).cloned()
    }
    
    fn update_setting(&mut self, key: String, value: String) {
        self.settings.insert(key, value);
        self.version += 1;
    }
}

fn config_cache_example() {
    let config = Arc::new(RwLock::new(Config::new()));
    let mut handles = vec![];
    
    // 多個讀者執行緒
    for i in 0..5 {
        let config = Arc::clone(&config);
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let reader = config.read().unwrap();
                let theme = reader.get_setting("theme").unwrap_or_default();
                println!("讀者 {} 第 {} 次: theme={}", i, j, theme);
                drop(reader);
                thread::sleep(Duration::from_millis(100));
            }
        });
        handles.push(handle);
    }
    
    // 寫者執行緒
    for i in 0..2 {
        let config = Arc::clone(&config);
        let handle = thread::spawn(move || {
            thread::sleep(Duration::from_millis(200));
            let mut writer = config.write().unwrap();
            let new_theme = if i == 0 { "light" } else { "auto" };
            writer.update_setting("theme".to_string(), new_theme.to_string());
            println!("寫者 {} 更新主題為: {}", i, new_theme);
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

fn performance_comparison() {
    use std::time::Instant;
    
    let iterations = 10000;
    let thread_count = 4;
    
    // Mutex 測試
    let mutex_data = Arc::new(Mutex::new(0));
    let start = Instant::now();
    
    let mut handles = vec![];
    for _ in 0..thread_count {
        let data = Arc::clone(&mutex_data);
        let handle = thread::spawn(move || {
            for _ in 0..iterations {
                let _guard = data.lock().unwrap();
                // 模擬讀取操作
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    let mutex_time = start.elapsed();
    
    // RwLock 測試
    let rwlock_data = Arc::new(RwLock::new(0));
    let start = Instant::now();
    
    let mut handles = vec![];
    for _ in 0..thread_count {
        let data = Arc::clone(&rwlock_data);
        let handle = thread::spawn(move || {
            for _ in 0..iterations {
                let _guard = data.read().unwrap();
                // 模擬讀取操作
            }
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    let rwlock_time = start.elapsed();
    
    println!("Mutex 時間: {:?}", mutex_time);
    println!("RwLock 時間: {:?}", rwlock_time);
    println!("RwLock 比 Mutex 快 {:.2}x", 
        mutex_time.as_nanos() as f64 / rwlock_time.as_nanos() as f64);
}

fn main() {
    println!("=== Config Cache Example ===");
    config_cache_example();
    
    println!("\n=== Performance Comparison ===");
    performance_comparison();
}