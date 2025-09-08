use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_double, c_int};

/// Rust 版本的加法函數
#[no_mangle]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    a + b
}

/// Rust 版本的乘法函數
#[no_mangle]
pub extern "C" fn rust_multiply(a: c_int, b: c_int) -> c_int {
    a * b
}

/// 計算平方根
#[no_mangle]
pub extern "C" fn rust_sqrt(x: c_double) -> c_double {
    x.sqrt()
}

/// 判斷是否為質數
#[no_mangle]
pub extern "C" fn rust_is_prime(n: c_int) -> c_int {
    if n <= 1 {
        return 0;
    }
    
    let n = n as u32;
    for i in 2..=((n as f64).sqrt() as u32) {
        if n % i == 0 {
            return 0;
        }
    }
    1
}

/// 生成問候語
/// 返回的字串需要呼叫者釋放
#[no_mangle]
pub extern "C" fn rust_greet(name: *const c_char) -> *mut c_char {
    unsafe {
        if name.is_null() {
            return std::ptr::null_mut();
        }
        
        let name_str = match CStr::from_ptr(name).to_str() {
            Ok(s) => s,
            Err(_) => return std::ptr::null_mut(),
        };
        
        let greeting = format!("Hello, {} from Rust!", name_str);
        
        match CString::new(greeting) {
            Ok(c_string) => c_string.into_raw(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

/// 釋放 Rust 分配的字串
#[no_mangle]
pub extern "C" fn rust_free_string(s: *mut c_char) {
    unsafe {
        if s.is_null() {
            return;
        }
        // 重新獲得字串的所有權並讓它自動釋放
        let _ = CString::from_raw(s);
    }
}

/// 計算陣列的平均值
#[no_mangle]
pub extern "C" fn rust_array_average(arr: *const c_double, size: c_int) -> c_double {
    if arr.is_null() || size <= 0 {
        return 0.0;
    }
    
    unsafe {
        let slice = std::slice::from_raw_parts(arr, size as usize);
        let sum: c_double = slice.iter().sum();
        sum / (size as c_double)
    }
}

/// 找出陣列中的最大值
#[no_mangle]
pub extern "C" fn rust_array_max(arr: *const c_int, size: c_int) -> c_int {
    if arr.is_null() || size <= 0 {
        return std::i32::MIN;
    }
    
    unsafe {
        let slice = std::slice::from_raw_parts(arr, size as usize);
        *slice.iter().max().unwrap_or(&std::i32::MIN)
    }
}

/// 字串長度計算（UTF-8 字元數）
#[no_mangle]
pub extern "C" fn rust_utf8_char_count(s: *const c_char) -> c_int {
    unsafe {
        if s.is_null() {
            return 0;
        }
        
        match CStr::from_ptr(s).to_str() {
            Ok(str) => str.chars().count() as c_int,
            Err(_) => -1, // 返回 -1 表示無效的 UTF-8
        }
    }
}

/// 簡單的結構體範例
#[repr(C)]
pub struct RustVector {
    x: c_double,
    y: c_double,
}

/// 創建向量
#[no_mangle]
pub extern "C" fn rust_create_vector(x: c_double, y: c_double) -> RustVector {
    RustVector { x, y }
}

/// 計算向量長度
#[no_mangle]
pub extern "C" fn rust_vector_length(v: RustVector) -> c_double {
    (v.x * v.x + v.y * v.y).sqrt()
}

/// 向量相加
#[no_mangle]
pub extern "C" fn rust_vector_add(v1: RustVector, v2: RustVector) -> RustVector {
    RustVector {
        x: v1.x + v2.x,
        y: v1.y + v2.y,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_rust_add() {
        assert_eq!(rust_add(2, 3), 5);
    }
    
    #[test]
    fn test_rust_is_prime() {
        assert_eq!(rust_is_prime(2), 1);
        assert_eq!(rust_is_prime(17), 1);
        assert_eq!(rust_is_prime(4), 0);
        assert_eq!(rust_is_prime(1), 0);
    }
    
    #[test]
    fn test_rust_sqrt() {
        assert_eq!(rust_sqrt(4.0), 2.0);
        assert_eq!(rust_sqrt(9.0), 3.0);
    }
}