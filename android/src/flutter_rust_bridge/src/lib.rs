use std::ffi::{CString, CStr};
use std::os::raw::c_char;
use serde::{Deserialize, Serialize};
use log::{info, warn, error, debug};
use std::sync::Once;

static INIT: Once = Once::new();

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct Message {
    pub id: u32,
    pub content: String,
    pub timestamp: u64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Response {
    pub success: bool,
    pub data: Option<String>,
    pub error: Option<String>,
}

fn init_logger() {
    INIT.call_once(|| {
        #[cfg(target_os = "android")]
        android_logger::init_once(
            android_logger::Config::default()
                .with_max_level(log::LevelFilter::Debug)
                .with_tag("BitoPro")
        );
        
        #[cfg(not(target_os = "android"))]
        env_logger::init();
        
        info!("[BitoPro] Rust logger initialized successfully");
    });
}

#[no_mangle]
pub extern "C" fn rust_add_numbers(a: i32, b: i32) -> i32 {
    init_logger();
    debug!("[BitoPro] rust_add_numbers called with a={}, b={}", a, b);
    
    let result = a + b;
    info!("[BitoPro] Addition result: {} + {} = {}", a, b, result);
    result
}

#[no_mangle]
pub extern "C" fn rust_process_message(json_str: *const c_char) -> *mut c_char {
    init_logger();
    info!("[BitoPro] rust_process_message called");
    
    if json_str.is_null() {
        error!("[BitoPro] Null pointer provided to rust_process_message");
        let error_response = Response {
            success: false,
            data: None,
            error: Some("Null pointer provided".to_string()),
        };
        return string_to_c_char(serde_json::to_string(&error_response).unwrap());
    }

    let c_str = unsafe { CStr::from_ptr(json_str) };
    let rust_str = match c_str.to_str() {
        Ok(s) => {
            debug!("[BitoPro] Received JSON string: {}", s);
            s
        },
        Err(e) => {
            error!("[BitoPro] Invalid UTF-8 string: {:?}", e);
            let error_response = Response {
                success: false,
                data: None,
                error: Some("Invalid UTF-8 string".to_string()),
            };
            return string_to_c_char(serde_json::to_string(&error_response).unwrap());
        }
    };

    match serde_json::from_str::<Message>(rust_str) {
        Ok(message) => {
            info!("[BitoPro] Successfully parsed message: id={}, content='{}', timestamp={}", 
                  message.id, message.content, message.timestamp);
            
            let processed_content = format!("[BitoPro] Processed: {}", message.content);
            let response = Response {
                success: true,
                data: Some(processed_content),
                error: None,
            };
            
            let response_json = serde_json::to_string(&response).unwrap();
            debug!("[BitoPro] Returning response: {}", response_json);
            string_to_c_char(response_json)
        }
        Err(e) => {
            error!("[BitoPro] JSON parsing error: {}", e);
            let error_response = Response {
                success: false,
                data: None,
                error: Some(format!("JSON parsing error: {}", e)),
            };
            string_to_c_char(serde_json::to_string(&error_response).unwrap())
        }
    }
}

#[no_mangle]
pub extern "C" fn rust_get_system_info() -> *mut c_char {
    init_logger();
    info!("[BitoPro] rust_get_system_info called");
    
    let info = format!(
        "[BitoPro] Rust Version: {}, OS: {}, Arch: {}",
        env!("CARGO_PKG_VERSION"),
        std::env::consts::OS,
        std::env::consts::ARCH
    );
    
    debug!("[BitoPro] System info: {}", info);
    string_to_c_char(info)
}

#[no_mangle]
pub extern "C" fn rust_free_string(ptr: *mut c_char) {
    init_logger();
    if !ptr.is_null() {
        debug!("[BitoPro] Freeing string memory at pointer: {:p}", ptr);
        unsafe {
            let _ = CString::from_raw(ptr);
        }
        debug!("[BitoPro] String memory freed successfully");
    } else {
        warn!("[BitoPro] Attempted to free null pointer");
    }
}

fn string_to_c_char(s: String) -> *mut c_char {
    match CString::new(s) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CStr;

    #[test]
    fn test_rust_add_numbers() {
        assert_eq!(rust_add_numbers(5, 3), 8);
        assert_eq!(rust_add_numbers(-2, 7), 5);
        assert_eq!(rust_add_numbers(0, 0), 0);
    }

    #[test]
    fn test_rust_process_message_valid_json() {
        let message = Message {
            id: 1,
            content: "Hello from test".to_string(),
            timestamp: 1234567890,
        };
        let json_str = serde_json::to_string(&message).unwrap();
        let c_json = CString::new(json_str).unwrap();
        
        let result_ptr = rust_process_message(c_json.as_ptr());
        assert!(!result_ptr.is_null());
        
        let result_c_str = unsafe { CStr::from_ptr(result_ptr) };
        let result_str = result_c_str.to_str().unwrap();
        let response: Response = serde_json::from_str(result_str).unwrap();
        
        assert!(response.success);
        assert!(response.data.is_some());
        assert!(response.data.unwrap().contains("Processed: Hello from test"));
        
        rust_free_string(result_ptr);
    }

    #[test]
    fn test_rust_process_message_invalid_json() {
        let invalid_json = CString::new("invalid json").unwrap();
        let result_ptr = rust_process_message(invalid_json.as_ptr());
        assert!(!result_ptr.is_null());
        
        let result_c_str = unsafe { CStr::from_ptr(result_ptr) };
        let result_str = result_c_str.to_str().unwrap();
        let response: Response = serde_json::from_str(result_str).unwrap();
        
        assert!(!response.success);
        assert!(response.error.is_some());
        
        rust_free_string(result_ptr);
    }

    #[test]
    fn test_rust_process_message_null_pointer() {
        let result_ptr = rust_process_message(std::ptr::null());
        assert!(!result_ptr.is_null());
        
        let result_c_str = unsafe { CStr::from_ptr(result_ptr) };
        let result_str = result_c_str.to_str().unwrap();
        let response: Response = serde_json::from_str(result_str).unwrap();
        
        assert!(!response.success);
        assert_eq!(response.error, Some("Null pointer provided".to_string()));
        
        rust_free_string(result_ptr);
    }

    #[test]
    fn test_rust_get_system_info() {
        let result_ptr = rust_get_system_info();
        assert!(!result_ptr.is_null());
        
        let result_c_str = unsafe { CStr::from_ptr(result_ptr) };
        let result_str = result_c_str.to_str().unwrap();
        
        assert!(result_str.contains("Rust Version"));
        assert!(result_str.contains("OS:"));
        assert!(result_str.contains("Arch:"));
        
        rust_free_string(result_ptr);
    }

    #[test]
    fn test_memory_management() {
        for _ in 0..1000 {
            let message = Message {
                id: 1,
                content: "Memory test".to_string(),
                timestamp: 1234567890,
            };
            let json_str = serde_json::to_string(&message).unwrap();
            let c_json = CString::new(json_str).unwrap();
            
            let result_ptr = rust_process_message(c_json.as_ptr());
            rust_free_string(result_ptr);
        }
    }
}