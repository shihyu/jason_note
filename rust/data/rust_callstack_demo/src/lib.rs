use std::sync::Mutex;
use once_cell::sync::Lazy;

pub static TEST_OUTPUT: Lazy<Mutex<Vec<String>>> = Lazy::new(|| Mutex::new(Vec::new()));

#[macro_export]
macro_rules! test_trace_call {
    () => {
        let bt = backtrace::Backtrace::new();
        let frames = bt.frames();
        
        let current_fn = {
            let mut name = String::from("unknown");
            if frames.len() > 1 {
                for symbol in frames[1].symbols() {
                    if let Some(n) = symbol.name() {
                        name = n.to_string();
                        break;
                    }
                }
            }
            name
        };
        
        let caller_fn = {
            let mut name = String::from("unknown");
            if frames.len() > 2 {
                for symbol in frames[2].symbols() {
                    if let Some(n) = symbol.name() {
                        name = n.to_string();
                        break;
                    }
                }
            }
            name
        };
        
        let output = format!("Entering: {} (called from: {})", 
                           current_fn.split("::").last().unwrap_or(&current_fn),
                           caller_fn.split("::").last().unwrap_or(&caller_fn));
        
        $crate::TEST_OUTPUT.lock().unwrap().push(output.clone());
        println!("{}", output);
    };
}

#[cfg(test)]
mod tests {
    use super::*;
    
    fn test_function_a() {
        test_trace_call!();
        test_function_b();
    }
    
    fn test_function_b() {
        test_trace_call!();
        test_function_c();
    }
    
    fn test_function_c() {
        test_trace_call!();
    }
    
    #[test]
    fn test_callstack_tracking() {
        let mut output_guard = TEST_OUTPUT.lock().unwrap();
        output_guard.clear();
        drop(output_guard);
        
        test_function_a();
        
        let output = TEST_OUTPUT.lock().unwrap();
        
        assert_eq!(output.len(), 3, "Should have 3 function calls tracked");
        
        assert!(output[0].contains("test_function_a"), 
                "First call should be test_function_a, got: {}", output[0]);
        assert!(output[0].contains("called from: test_callstack_tracking"), 
                "test_function_a should be called from test_callstack_tracking");
        
        assert!(output[1].contains("test_function_b"), 
                "Second call should be test_function_b");
        assert!(output[1].contains("called from: test_function_a"), 
                "test_function_b should be called from test_function_a");
        
        assert!(output[2].contains("test_function_c"), 
                "Third call should be test_function_c");
        assert!(output[2].contains("called from: test_function_b"), 
                "test_function_c should be called from test_function_b");
    }
    
    #[test]
    fn test_recursive_tracking() {
        let mut output_guard = TEST_OUTPUT.lock().unwrap();
        output_guard.clear();
        drop(output_guard);
        
        fn recursive_test(depth: u32) {
            test_trace_call!();
            if depth > 0 {
                recursive_test(depth - 1);
            }
        }
        
        recursive_test(2);
        
        let output = TEST_OUTPUT.lock().unwrap();
        
        assert_eq!(output.len(), 3, "Should have 3 recursive calls");
        
        assert!(output[0].contains("recursive_test"));
        assert!(output[0].contains("called from: test_recursive_tracking"));
        
        assert!(output[1].contains("recursive_test"));
        assert!(output[1].contains("called from: recursive_test"));
        
        assert!(output[2].contains("recursive_test"));
        assert!(output[2].contains("called from: recursive_test"));
    }
    
    #[test]
    fn test_direct_call() {
        let mut output_guard = TEST_OUTPUT.lock().unwrap();
        output_guard.clear();
        drop(output_guard);
        
        test_function_c();
        
        let output = TEST_OUTPUT.lock().unwrap();
        
        assert_eq!(output.len(), 1, "Should have 1 function call");
        assert!(output[0].contains("test_function_c"));
        assert!(output[0].contains("called from: test_direct_call"));
    }
}