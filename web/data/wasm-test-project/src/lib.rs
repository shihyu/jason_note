use wasm_bindgen::prelude::*;

// 導入 console API
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
    #[wasm_bindgen(js_namespace = console)]
    fn error(s: &str);
    #[wasm_bindgen(js_namespace = console)]
    fn warn(s: &str);
    #[wasm_bindgen(js_namespace = console)]
    fn info(s: &str);
    #[wasm_bindgen(js_namespace = console, js_name = time)]
    fn console_time(s: &str);
    #[wasm_bindgen(js_namespace = console, js_name = timeEnd)]
    fn console_time_end(s: &str);
}

// 日誌宏
macro_rules! console_log {
    ($($t:tt)*) => (log(&format!("[WASM LOG] {}", format_args!($($t)*))))
}
macro_rules! console_error {
    ($($t:tt)*) => (error(&format!("[WASM ERROR] {}", format_args!($($t)*))))
}
macro_rules! console_warn {
    ($($t:tt)*) => (warn(&format!("[WASM WARN] {}", format_args!($($t)*))))
}
macro_rules! console_info {
    ($($t:tt)*) => (info(&format!("[WASM INFO] {}", format_args!($($t)*))))
}

// 初始化函數
#[wasm_bindgen(start)]
pub fn main() {
    console_log!("WASM 模組已載入，版本: optimized-debug");
    console_log!("初始化完成，準備接收測試請求");
}

// 基本測試函數
#[wasm_bindgen]
pub fn test_basic_math(a: i32, b: i32) -> i32 {
    console_log!("執行基本數學運算: {} + {}", a, b);
    let result = a + b;
    console_log!("計算結果: {}", result);
    result
}

// 字符串處理測試
#[wasm_bindgen]
pub fn test_string_processing(input: &str) -> String {
    console_log!("處理字符串: '{}'", input);
    let processed = format!("PROCESSED: {}", input.to_uppercase());
    console_log!("處理後: '{}'", processed);
    processed
}

// 重計算測試
#[wasm_bindgen]
pub fn test_heavy_computation(n: i32) -> i32 {
    console_time("heavy_computation");
    console_log!("開始重計算，參數: {}", n);
    
    let mut result = 0;
    for i in 0..n {
        result += i * i;
        if i % 1000 == 0 {
            console_log!("計算進度: {} / {}", i, n);
        }
    }
    
    console_log!("重計算完成，結果: {}", result);
    console_time_end("heavy_computation");
    result
}

// 數組處理測試
#[wasm_bindgen]
pub fn test_array_processing(data: &[i32]) -> Vec<i32> {
    console_log!("處理數組，長度: {}", data.len());
    
    let mut processed: Vec<i32> = data.iter().map(|x| x * 2).collect();
    processed.sort();
    
    console_log!("數組處理完成，新長度: {}", processed.len());
    if !processed.is_empty() {
        console_log!("範圍: {} ~ {}", processed[0], processed[processed.len() - 1]);
    }
    
    processed
}

// 錯誤處理測試
#[wasm_bindgen]
pub fn test_error_handling(should_fail: bool) -> Result<String, JsValue> {
    console_log!("測試錯誤處理，should_fail: {}", should_fail);
    
    if should_fail {
        console_error!("故意觸發錯誤");
        Err(JsValue::from_str("這是一個測試錯誤"))
    } else {
        console_log!("正常執行路徑");
        Ok("成功執行".to_string())
    }
}

// 性能基準測試
#[wasm_bindgen]
pub fn test_performance_benchmark() -> f64 {
    console_time("performance_benchmark");
    console_log!("開始性能基準測試");
    
    let start = js_sys::Date::now();
    
    // 執行一些計算密集型操作
    let mut sum = 0f64;
    for i in 0..100000 {
        sum += (i as f64).sqrt();
    }
    
    let duration = js_sys::Date::now() - start;
    console_log!("基準測試完成，耗時: {:.2}ms，計算和: {:.2}", duration, sum);
    console_time_end("performance_benchmark");
    
    duration
}

// 內存信息
#[wasm_bindgen]
pub fn get_memory_info() -> String {
    // 使用 WebAssembly.Memory API
    let memory_size = 64 * 1024; // 假設的內存頁面大小
    let info = format!("WASM 內存頁面: {} bytes", memory_size);
    console_log!("{}", info);
    info
}

// 調試輔助函數
#[wasm_bindgen]
pub fn debug_trace(message: &str) {
    console_log!("[DEBUG TRACE] {}", message);
}

// 測試所有功能
#[wasm_bindgen]
pub fn run_all_tests() -> String {
    console_log!("=== 開始執行所有測試 ===");
    
    let mut results = Vec::new();
    
    // 測試 1: 基本數學
    let math_result = test_basic_math(42, 8);
    results.push(format!("數學測試: {}", math_result));
    
    // 測試 2: 字符串處理
    let string_result = test_string_processing("hello world");
    results.push(format!("字符串測試: {}", string_result));
    
    // 測試 3: 重計算
    let heavy_result = test_heavy_computation(5000);
    results.push(format!("重計算測試: {}", heavy_result));
    
    // 測試 4: 數組處理
    let array_data = vec![3, 1, 4, 1, 5, 9, 2, 6];
    let array_result = test_array_processing(&array_data);
    results.push(format!("數組測試: {:?}", array_result));
    
    // 測試 5: 錯誤處理
    match test_error_handling(false) {
        Ok(msg) => results.push(format!("錯誤處理測試: {}", msg)),
        Err(_) => results.push("錯誤處理測試: 失敗".to_string()),
    }
    
    // 測試 6: 性能基準
    let perf_result = test_performance_benchmark();
    results.push(format!("性能測試: {:.2}ms", perf_result));
    
    // 測試 7: 內存信息
    let memory_info = get_memory_info();
    results.push(format!("內存測試: {}", memory_info));
    
    let summary = results.join("; ");
    console_log!("=== 所有測試完成 ===");
    console_log!("結果摘要: {}", summary);
    
    summary
}