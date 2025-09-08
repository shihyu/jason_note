use std::ffi::CString;
use std::os::raw::{c_char, c_int};

// 定義 Point 結構體，與 C 的結構體對應
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct Point {
    x: c_int,
    y: c_int,
}

// 聲明外部 C 函數
#[link(name = "math")]
extern "C" {
    // 基本數學運算
    fn add(a: c_int, b: c_int) -> c_int;
    fn factorial(n: c_int) -> c_int;
    fn fibonacci(n: c_int) -> c_int;
    
    // 字串操作
    fn say_hello(name: *const c_char);
    fn reverse_string(str: *mut c_char);
    
    // 陣列操作
    fn sum_array(arr: *const c_int, size: c_int) -> c_int;
    
    // 結構體相關函數
    fn create_point(x: c_int, y: c_int) -> Point;
    fn manhattan_distance(p1: Point, p2: Point) -> c_int;
}

fn test_basic_math() {
    println!("=== 測試基本數學運算 ===");
    
    unsafe {
        // 測試加法
        let result = add(10, 20);
        println!("add(10, 20) = {}", result);
        assert_eq!(result, 30, "加法測試失敗");
        
        // 測試階乘
        let fact = factorial(5);
        println!("factorial(5) = {}", fact);
        assert_eq!(fact, 120, "階乘測試失敗");
        
        // 測試斐波那契
        let fib = fibonacci(10);
        println!("fibonacci(10) = {}", fib);
        assert_eq!(fib, 55, "斐波那契測試失敗");
    }
    
    println!("✓ 基本數學運算測試通過\n");
}

fn test_string_operations() {
    println!("=== 測試字串操作 ===");
    
    unsafe {
        // 測試打招呼
        let name = CString::new("Rust").unwrap();
        say_hello(name.as_ptr());
        
        // 測試字串反轉
        let mut test_str = CString::new("Hello World").unwrap().into_bytes_with_nul();
        println!("原始字串: {}", String::from_utf8_lossy(&test_str[..test_str.len()-1]));
        
        reverse_string(test_str.as_mut_ptr() as *mut c_char);
        
        let reversed = CString::from_vec_with_nul(test_str).unwrap();
        println!("反轉後: {}", reversed.to_string_lossy());
        assert_eq!(reversed.to_bytes(), b"dlroW olleH", "字串反轉測試失敗");
    }
    
    println!("✓ 字串操作測試通過\n");
}

fn test_array_operations() {
    println!("=== 測試陣列操作 ===");
    
    unsafe {
        // 創建整數陣列
        let arr = vec![1, 2, 3, 4, 5];
        
        // 計算陣列總和
        let total = sum_array(arr.as_ptr(), arr.len() as c_int);
        println!("陣列 {:?} 的總和 = {}", arr, total);
        assert_eq!(total, 15, "陣列總和測試失敗");
    }
    
    println!("✓ 陣列操作測試通過\n");
}

fn test_struct_operations() {
    println!("=== 測試結構體操作 ===");
    
    unsafe {
        // 創建點
        let p1 = create_point(3, 4);
        let p2 = create_point(6, 8);
        
        println!("點1: ({}, {})", p1.x, p1.y);
        println!("點2: ({}, {})", p2.x, p2.y);
        
        // 計算曼哈頓距離
        let distance = manhattan_distance(p1, p2);
        println!("曼哈頓距離 = {}", distance);
        assert_eq!(distance, 7, "曼哈頓距離測試失敗");
    }
    
    println!("✓ 結構體操作測試通過\n");
}

fn main() {
    println!("Rust FFI 範例 - 調用 C 函數庫\n");
    
    test_basic_math();
    test_string_operations();
    test_array_operations();
    test_struct_operations();
    
    println!("========================================");
    println!("✅ 所有測試通過！");
    println!("========================================");
}