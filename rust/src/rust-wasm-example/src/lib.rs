// lib.rs
use wasm_bindgen::prelude::*;

// 導出給 JavaScript 使用的函數
#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 導出一個簡單的字符串處理函數
#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("你好, {}!", name)
}

// 導出一個結構體和相關方法
#[wasm_bindgen]
pub struct Counter {
    count: i32,
}

#[wasm_bindgen]
impl Counter {
    pub fn new() -> Counter {
        Counter { count: 0 }
    }

    pub fn increment(&mut self) {
        self.count += 1;
    }

    pub fn value(&self) -> i32 {
        self.count
    }
}
