// C++ Move 語義 vs Rust 所有權系統 深度對比
// =============================================

/*
核心差異總結：

C++ Move:
- 運行時優化機制
- 可選的，編譯器決定
- 移動後對象仍存在但處於"已移動"狀態
- 可能意外訪問已移動對象
- 需要程序員理解和正確使用

Rust Ownership:
- 編譯時強制的內存安全機制
- 必須的，編譯器強制執行
- 移動後原變量不可再訪問
- 編譯器防止任何誤用
- 自動處理，零運行時開銷
*/

// ============================================
// 1. 基本概念對比
// ============================================

/* C++ Move 語義示例:

#include <iostream>
#include <vector>
#include <string>
#include <utility>

class Resource {
private:
    std::vector<int> data;
    std::string name;
    
public:
    // 構造函數
    Resource(const std::string& n) : name(n) {
        data.resize(1000, 42);
        std::cout << "資源 " << name << " 創建\n";
    }
    
    // 複製構造函數
    Resource(const Resource& other) : data(other.data), name(other.name + "_copy") {
        std::cout << "資源 " << name << " 被複製\n";
    }
    
    // 移動構造函數
    Resource(Resource&& other) noexcept 
        : data(std::move(other.data)), name(std::move(other.name)) {
        std::cout << "資源 " << name << " 被移動\n";
        // other 仍然存在，但資源已被"偷走"
    }
    
    // 複製賦值
    Resource& operator=(const Resource& other) {
        if (this != &other) {
            data = other.data;
            name = other.name + "_assigned";
            std::cout << "資源 " << name << " 被賦值複製\n";
        }
        return *this;
    }
    
    // 移動賦值
    Resource& operator=(Resource&& other) noexcept {
        if (this != &other) {
            data = std::move(other.data);
            name = std::move(other.name);
            std::cout << "資源 " << name << " 被賦值移動\n";
        }
        return *this;
    }
    
    ~Resource() {
        std::cout << "資源 " << name << " 被銷毀\n";
    }
    
    void use_resource() {
        std::cout << "使用資源 " << name << " (大小: " << data.size() << ")\n";
    }
};

void cpp_move_examples() {
    std::cout << "=== C++ Move 語義 ===\n";
    
    // 1. 基本移動
    Resource r1("original");
    Resource r2 = std::move(r1);  // 移動構造
    
    // 危險：r1 仍然存在但已被移動，訪問可能導致未定義行為
    // r1.use_resource();  // 可能崩潰或產生錯誤結果
    
    r2.use_resource();  // 安全
    
    // 2. 函數參數移動
    auto create_resource = []() -> Resource {
        return Resource("temp");  // 自動移動（RVO可能跳過）
    };
    
    Resource r3 = create_resource();  // 移動或複製
    
    // 3. 容器中的移動
    std::vector<Resource> resources;
    resources.push_back(std::move(r2));  // 移動到容器中
    // r2 現在處於已移動狀態
    
    // 4. 錯誤：意外使用已移動對象
    // r2.use_resource();  // 未定義行為！
}

int main() {
    cpp_move_examples();
    return 0;
}

*/

// Rust 所有權系統 - 相同功能的安全實現
use std::fmt;

#[derive(Debug)]
struct Resource {
    data: Vec<i32>,
    name: String,
}

impl Resource {
    fn new(name: &str) -> Self {
        println!("資源 {} 創建", name);
        Resource {
            data: vec![42; 1000],
            name: name.to_string(),
        }
    }
    
    fn use_resource(&self) {
        println!("使用資源 {} (大小: {})", self.name, self.data.len());
    }
    
    fn use_resource_mut(&mut self) {
        self.data.push(99);
        println!("修改資源 {} (新大小: {})", self.name, self.data.len());
    }
}

impl Drop for Resource {
    fn drop(&mut self) {
        println!("資源 {} 被銷毀", self.name);
    }
}

impl Clone for Resource {
    fn clone(&self) -> Self {
        println!("資源 {} 被克隆", self.name);
        Resource {
            data: self.data.clone(),
            name: format!("{}_clone", self.name),
        }
    }
}

fn rust_ownership_examples() {
    println!("=== Rust 所有權系統 ===");
    
    // 1. 基本移動（所有權轉移）
    let r1 = Resource::new("original");
    let r2 = r1;  // 所有權移動，r1 不再可用
    
    // 編譯錯誤：r1 已被移動
    // r1.use_resource();  // 編譯錯誤！
    
    r2.use_resource();  // 安全
    
    // 2. 函數參數所有權轉移
    fn take_ownership(resource: Resource) {
        resource.use_resource();
        // resource 在函數結束時被銷毀
    }
    
    fn borrow_resource(resource: &Resource) {
        resource.use_resource();
        // 只是借用，不獲取所有權
    }
    
    fn borrow_mut_resource(resource: &mut Resource) {
        resource.use_resource_mut();
        // 可變借用，可以修改但不獲取所有權
    }
    
    let r3 = Resource::new("for_function");
    
    // 選項1：轉移所有權
    // take_ownership(r3);  // r3 被移動，不再可用
    
    // 選項2：借用（推薦）
    borrow_resource(&r3);  // r3 仍然可用
    
    // 選項3：可變借用
    let mut r4 = Resource::new("mutable");
    borrow_mut_resource(&mut r4);
    r4.use_resource();  // 仍然可用
    
    // 3. 容器中的所有權
    let mut resources = Vec::new();
    let r5 = Resource::new("for_vector");
    resources.push(r5);  // r5 被移動到 vector 中
    // r5 不再可用
    
    // 訪問 vector 中的資源
    if let Some(resource) = resources.get(0) {
        resource.use_resource();
    }
    
    // 4. 所有權恢復
    let recovered = resources.pop().unwrap();  // 從 vector 中取回所有權
    recovered.use_resource();
}

// ============================================
// 2. 深度對比：複雜場景
// ============================================

/* C++ 複雜移動場景的問題:

class ComplexResource {
    std::unique_ptr<int[]> buffer;
    size_t size;
    std::string id;
    
public:
    ComplexResource(const std::string& identifier, size_t s) 
        : buffer(std::make_unique<int[]>(s)), size(s), id(identifier) {}
    
    // 移動構造後，原對象狀態不一致
    ComplexResource(ComplexResource&& other) noexcept
        : buffer(std::move(other.buffer)), size(other.size), id(std::move(other.id)) {
        // 問題：other.size 仍然保留原值，但 other.buffer 為 null
        // 這可能導致不一致狀態
    }
    
    void process() {
        if (buffer) {  // 必須檢查，因為可能已被移動
            for (size_t i = 0; i < size; ++i) {
                buffer[i] = i;
            }
        } else {
            // 已被移動的對象被意外使用
            std::cout << "錯誤：嘗試使用已移動的資源\n";
        }
    }
    
    size_t get_size() const { return size; }  // 可能返回錯誤信息
};

void problematic_move_usage() {
    ComplexResource cr1("test", 100);
    ComplexResource cr2 = std::move(cr1);
    
    // 危險：cr1 處於部分移動狀態
    std::cout << "cr1 size: " << cr1.get_size() << "\n";  // 仍然返回 100
    cr1.process();  // 但實際上 buffer 是 null！
}

*/

// Rust 等價實現 - 編譯時安全
struct ComplexResource {
    buffer: Vec<i32>,  // 自動管理內存
    id: String,
}

impl ComplexResource {
    fn new(identifier: &str, size: usize) -> Self {
        ComplexResource {
            buffer: vec![0; size],
            id: identifier.to_string(),
        }
    }
    
    fn process(&mut self) {
        for (i, item) in self.buffer.iter_mut().enumerate() {
            *item = i as i32;
        }
        println!("處理完成：{} 個元素", self.buffer.len());
    }
    
    fn get_size(&self) -> usize {
        self.buffer.len()
    }
    
    fn get_id(&self) -> &str {
        &self.id
    }
}

fn safe_ownership_usage() {
    let mut cr1 = ComplexResource::new("test", 100);
    let cr2 = cr1;  // 完整移動，cr1 完全不可用
    
    // 編譯錯誤：無法訪問已移動的變量
    // println!("cr1 size: {}", cr1.get_size());  // 編譯錯誤！
    // cr1.process();  // 編譯錯誤！
    
    println!("cr2 size: {}", cr2.get_size());  // 安全
    // cr2.process();  // 需要可變引用
}

// ============================================
// 3. 性能對比
// ============================================

fn performance_comparison() {
    use std::time::Instant;
    
    println!("\n=== 性能對比 ===");
    
    // 測試大量所有權轉移
    let start = Instant::now();
    
    let mut resources = Vec::new();
    for i in 0..10000 {
        let resource = Resource::new(&format!("resource_{}", i));
        resources.push(resource);  // 移動，零成本
    }
    
    // 處理所有資源
    for resource in &resources {
        resource.use_resource();
    }
    
    let duration = start.elapsed();
    println!("Rust 所有權轉移耗時: {:?}", duration);
    
    // 測試借用性能
    let start = Instant::now();
    
    fn process_by_reference(resources: &[Resource]) {
        for resource in resources {
            resource.use_resource();
        }
    }
    
    process_by_reference(&resources);
    
    let duration = start.elapsed();
    println!("Rust 借用處理耗時: {:?}", duration);
}

// ============================================
// 4. 錯誤處理和安全性
// ============================================

/* C++ 移動相關的常見錯誤:

void common_cpp_move_errors() {
    // 錯誤1：使用已移動對象
    std::vector<int> v1 = {1, 2, 3, 4, 5};
    std::vector<int> v2 = std::move(v1);
    std::cout << v1.size() << std::endl;  // 可能是0，但不保證
    
    // 錯誤2：移動後再次移動
    std::string s1 = "hello";
    std::string s2 = std::move(s1);
    std::string s3 = std::move(s1);  // 移動空字符串
    
    // 錯誤3：在條件語句中移動
    std::vector<int> data = {1, 2, 3};
    if (some_condition) {
        process(std::move(data));
    }
    // 如果條件為假，data 仍然可用，但如果為真則不可用
    data.push_back(4);  // 可能錯誤
    
    // 錯誤4：返回本地變量的移動
    auto create_vector = []() {
        std::vector<int> local = {1, 2, 3};
        return std::move(local);  // 不必要，反而可能阻止RVO
    };
}

*/

// Rust 編譯時防止這些錯誤
fn rust_compile_time_safety() {
    println!("\n=== Rust 編譯時安全檢查 ===");
    
    // 1. 防止使用已移動變量
    let v1 = vec![1, 2, 3, 4, 5];
    let v2 = v1;  // v1 被移動
    // println!("{}", v1.len());  // 編譯錯誤！
    println!("v2 長度: {}", v2.len());  // 安全
    
    // 2. 防止重複移動
    let s1 = String::from("hello");
    let s2 = s1;  // s1 被移動
    // let s3 = s1;  // 編譯錯誤！
    println!("s2: {}", s2);
    
    // 3. 條件移動的安全處理
    let data = vec![1, 2, 3];
    let some_condition = true;
    
    let processed_data = if some_condition {
        // 移動到函數中處理
        process_data(data)
    } else {
        // 如果不處理，保持原樣
        data
    };
    
    // processed_data 總是可用的
    println!("處理後數據長度: {}", processed_data.len());
    
    // 4. 返回值優化是自動的
    fn create_vector() -> Vec<i32> {
        let local = vec![1, 2, 3];
        local  // 自動移動，無需顯式 move
    }
    
    let result = create_vector();
    println!("創建的向量: {:?}", result);
}

fn process_data(mut data: Vec<i32>) -> Vec<i32> {
    data.push(4);
    data
}

// ============================================
// 5. 高級所有權模式
// ============================================

// 智能指針和共享所有權
use std::rc::Rc;
use std::cell::RefCell;
use std::sync::{Arc, Mutex};

fn advanced_ownership_patterns() {
    println!("\n=== 高級所有權模式 ===");
    
    // 1. 引用計數共享所有權 (單線程)
    {
        let shared_data = Rc::new(vec![1, 2, 3, 4, 5]);
        let reference1 = Rc::clone(&shared_data);
        let reference2 = Rc::clone(&shared_data);
        
        println!("引用計數: {}", Rc::strong_count(&shared_data));
        println!("共享數據: {:?}", shared_data);
        
        // 所有引用離開作用域時，數據自動釋放
    }
    
    // 2. 內部可變性
    {
        let data = Rc::new(RefCell::new(vec![1, 2, 3]));
        let ref1 = Rc::clone(&data);
        let ref2 = Rc::clone(&data);
        
        // 通過任何引用都可以修改
        ref1.borrow_mut().push(4);
        ref2.borrow_mut().push(5);
        
        println!("修改後的數據: {:?}", data.borrow());
    }
    
    // 3. 線程安全的共享所有權
    {
        let shared_counter = Arc::new(Mutex::new(0));
        let mut handles = vec![];
        
        for _ in 0..3 {
            let counter = Arc::clone(&shared_counter);
            let handle = std::thread::spawn(move || {
                let mut num = counter.lock().unwrap();
                *num += 1;
            });
            handles.push(handle);
        }
        
        for handle in handles {
            handle.join().unwrap();
        }
        
        println!("最終計數: {}", *shared_counter.lock().unwrap());
    }
}

// ============================================
// 6. 生命週期和借用
// ============================================

// 生命週期參數確保引用有效性
fn lifetime_examples() {
    println!("\n=== 生命週期示例 ===");
    
    // 1. 基本生命週期
    fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
        if x.len() > y.len() {
            x
        } else {
            y
        }
    }
    
    let string1 = String::from("long string");
    let string2 = "short";
    let result = longest(&string1, string2);
    println!("最長的字符串: {}", result);
    
    // 2. 結構體中的生命週期
    #[derive(Debug)]
    struct ImportantExcerpt<'a> {
        part: &'a str,
    }
    
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find a '.'");
    let excerpt = ImportantExcerpt {
        part: first_sentence,
    };
    println!("摘錄: {:?}", excerpt);
    
    // 3. 複雜借用場景
    fn demonstrate_borrowing() {
        let mut data = vec![1, 2, 3, 4, 5];
        
        // 不可變借用
        let sum: i32 = data.iter().sum();
        println!("總和: {}", sum);
        
        // 可變借用
        data.push(6);
        println!("添加元素後: {:?}", data);
        
        // 同時存在多個不可變借用
        let first = &data[0];
        let last = &data[data.len() - 1];
        println!("第一個: {}, 最後一個: {}", first, last);
        
        // 但不能同時存在可變和不可變借用
        // let mut_ref = &mut data;  // 編譯錯誤！
    }
    
    demonstrate_borrowing();
}

// ============================================
// 主函數和測試
// ============================================

fn main() {
    println!("🔄 C++ Move vs Rust Ownership 深度對比");
    println!("======================================");
    
    rust_ownership_examples();
    safe_ownership_usage();
    performance_comparison();
    rust_compile_time_safety();
    advanced_ownership_patterns();
    lifetime_examples();
    
    println!("\n📊 總結對比:");
    println!("=============");
    
    println!("C++ Move語義:");
    println!("  ✅ 性能優化，減少不必要的複製");
    println!("  ❌ 運行時概念，可能誤用已移動對象");
    println!("  ❌ 需要程序員手動管理移動語義");
    println!("  ❌ 移動後對象狀態可能不一致");
    
    println!("\nRust 所有權系統:");
    println!("  ✅ 編譯時保證內存安全");
    println!("  ✅ 零運行時開銷");
    println!("  ✅ 自動管理，無需手動干預");
    println!("  ✅ 移動後原變量完全不可訪問");
    println!("  ✅ 借用檢查器防止數據競爭");
    
    println!("\n🎯 關鍵區別:");
    println!("  • C++ Move: 優化機制，可選使用");
    println!("  • Rust Ownership: 安全機制，強制執行");
    println!("  • C++ 側重性能，Rust 側重安全");
    println!("  • C++ 運行時檢查，Rust 編譯時檢查");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_ownership_transfer() {
        let resource = Resource::new("test");
        let moved_resource = resource;
        
        // 確保移動後可以正常使用
        moved_resource.use_resource();
        
        // 以下會編譯失敗，證明所有權已轉移
        // resource.use_resource();
    }
    
    #[test]
    fn test_borrowing() {
        let resource = Resource::new("test");
        
        // 多次借用應該都可以工作
        fn use_resource_ref(r: &Resource) {
            r.use_resource();
        }
        
        use_resource_ref(&resource);
        use_resource_ref(&resource);
        
        // 原始變量仍然可用
        resource.use_resource();
    }
    
    #[test]
    fn test_mutable_borrowing() {
        let mut resource = Resource::new("test");
        
        // 可變借用
        fn modify_resource(r: &mut Resource) {
            r.use_resource_mut();
        }
        
        modify_resource(&mut resource);
        
        // 借用結束後仍可使用
        resource.use_resource();
    }
}
