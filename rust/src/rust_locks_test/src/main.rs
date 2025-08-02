use std::process::Command;

fn main() {
    println!("🦀 Rust 鎖機制指南 - 測試所有範例");
    println!("=====================================\n");

    let examples = vec![
        ("mutex_examples", "Arc<Mutex<T>> 基本互斥鎖"),
        ("rwlock_examples", "Arc<RwLock<T>> 讀寫鎖"),
        ("atomic_examples", "Atomic 原子類型"),
        ("channel_examples", "Channel 通道"),
        ("condvar_examples", "Condvar 條件變數"),
        ("refcell_examples", "Rc<RefCell<T>> 單執行緒共享"),
        // Skip advanced_examples as it takes too long
    ];

    for (example, description) in examples {
        println!("🔄 測試 {} - {}", example, description);
        println!("---");
        
        match Command::new("cargo")
            .args(["run", "--bin", example])
            .output()
        {
            Ok(output) => {
                if output.status.success() {
                    println!("✅ {} 測試成功！", description);
                    println!("{}", String::from_utf8_lossy(&output.stdout));
                } else {
                    println!("❌ {} 測試失敗！", description);
                    println!("錯誤輸出:");
                    println!("{}", String::from_utf8_lossy(&output.stderr));
                }
            }
            Err(e) => {
                println!("❌ 無法執行 {}: {}", example, e);
            }
        }
        
        println!("\n{}\n", "=".repeat(50));
    }

    println!("🎉 所有範例測試完成！");
}