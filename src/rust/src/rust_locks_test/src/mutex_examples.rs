use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

fn basic_example() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for i in 0..5 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            for _ in 0..1000 {
                let mut num = counter.lock().unwrap();
                *num += 1;
            }
            println!("執行緒 {} 完成", i);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最終計數: {}", *counter.lock().unwrap());
}

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
    }
}

fn shared_data_example() {
    let data = Arc::new(Mutex::new(SharedData::new()));
    let mut handles = vec![];

    for i in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            for j in 0..3 {
                let item = format!("執行緒{}-項目{}", i, j);
                {
                    let mut shared = data.lock().unwrap();
                    shared.add_item(item.clone());
                    println!("新增: {}", item);
                }
                thread::sleep(Duration::from_millis(100));
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("最終資料: {:?}", *data.lock().unwrap());
}

fn poison_handling_example() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    let data_clone = Arc::clone(&data);
    
    // 建立會 panic 的執行緒
    let handle = thread::spawn(move || {
        let mut vec = data_clone.lock().unwrap();
        vec.push(4);
        panic!("故意的 panic!");
    });
    
    let _ = handle.join();
    
    // 處理毒化的 Mutex
    match data.lock() {
        Ok(vec) => println!("成功獲取: {:?}", *vec),
        Err(poisoned) => {
            println!("Mutex 被毒化了！");
            let vec = poisoned.into_inner();
            println!("強制獲取的資料: {:?}", *vec);
        }
    };
}

// 安全的 Mutex 存取包裝器
fn safe_mutex_access<T, F, R>(mutex: &Mutex<T>, f: F) -> Result<R, String>
where
    F: FnOnce(&mut T) -> R,
{
    match mutex.lock() {
        Ok(mut guard) => Ok(f(&mut guard)),
        Err(poisoned) => {
            eprintln!("警告: Mutex 被毒化，嘗試恢復...");
            let mut guard = poisoned.into_inner();
            Ok(f(&mut guard))
        }
    }
}

fn safe_wrapper_example() {
    let data = Arc::new(Mutex::new(42));
    
    match safe_mutex_access(&data, |value| {
        *value += 1;
        *value
    }) {
        Ok(result) => println!("操作成功，新值: {}", result),
        Err(e) => println!("操作失敗: {}", e),
    }
}

fn main() {
    println!("=== Basic Mutex Example ===");
    basic_example();
    
    println!("\n=== Shared Data Example ===");
    shared_data_example();
    
    println!("\n=== Poison Handling Example ===");
    poison_handling_example();
    
    println!("\n=== Safe Wrapper Example ===");
    safe_wrapper_example();
}