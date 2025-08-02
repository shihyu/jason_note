// 錯誤處理與毒化機制 - Mutex 的健壯性處理
// 演示如何處理 Mutex 毒化和錯誤恢復

use std::sync::{Arc, Mutex};
use std::thread;

// 安全的 Mutex 存取包裝器
fn safe_mutex_access<T, F, R>(mutex: &Mutex<T>, f: F) -> Result<R, String>
where
    F: FnOnce(&mut T) -> R,
{
    match mutex.lock() {
        Ok(mut guard) => Ok(f(&mut guard)),
        Err(poisoned) => {
            eprintln!("⚠️  警告: Mutex 被毒化，嘗試恢復...");
            let mut guard = poisoned.into_inner();
            Ok(f(&mut guard))
        }
    }
}

fn main() {
    println!("🚨 Mutex 錯誤處理與毒化機制範例");
    println!("====================================");
    
    poison_handling_demo();
    println!("\n{}", "=".repeat(40));
    safe_wrapper_demo();
}

fn poison_handling_demo() {
    println!("🧪 毒化處理示範:");
    
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    let data_clone = Arc::clone(&data);
    
    // 建立會 panic 的執行緒
    let handle = thread::spawn(move || {
        let mut vec = data_clone.lock().unwrap();
        vec.push(4);
        println!("💥 即將觸發 panic!");
        panic!("故意的 panic 來演示毒化機制!");
    });
    
    // 等待執行緒完成（會 panic）
    let _ = handle.join();
    
    // 處理毒化的 Mutex
    match data.lock() {
        Ok(vec) => println!("✅ 成功獲取: {:?}", *vec),
        Err(poisoned) => {
            println!("🔥 Mutex 被毒化了！");
            let vec = poisoned.into_inner();
            println!("🔧 強制獲取的資料: {:?}", *vec);
            println!("📝 注意：資料雖然被毒化，但仍然可以恢復");
        }
    };
}

fn safe_wrapper_demo() {
    println!("🛡️  安全包裝器示範:");
    
    let data = Arc::new(Mutex::new(42));
    
    match safe_mutex_access(&data, |value| {
        *value += 8;
        *value
    }) {
        Ok(result) => println!("✅ 操作成功，新值: {}", result),
        Err(e) => println!("❌ 操作失敗: {}", e),
    }
    
    println!("💡 提示：使用包裝器函數可以優雅地處理 Mutex 錯誤");
}