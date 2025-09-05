use backtrace::{Backtrace, BacktraceFrame};
use std::sync::Mutex;

static INDENT_LEVEL: Mutex<usize> = Mutex::new(0);

fn get_caller_name(frames: &[BacktraceFrame]) -> String {
    let skip_frames = [
        "trace_call",
        "get_caller_name",
        "Backtrace::new",
        "backtrace::",
        "std::",
        "core::",
        "rust_begin_unwind",
        "_start",
        "__libc_start",
    ];
    
    for frame in frames.iter().skip(2) {
        for symbol in frame.symbols() {
            if let Some(name) = symbol.name() {
                let full_name = name.to_string();
                
                let should_skip = skip_frames.iter().any(|&s| full_name.contains(s));
                if should_skip {
                    continue;
                }
                
                let parts: Vec<&str> = full_name.split("::").collect();
                if let Some(&last_part) = parts.last() {
                    if last_part.starts_with("h") && last_part.len() == 17 {
                        if parts.len() >= 2 {
                            return parts[parts.len() - 2].to_string();
                        }
                    } else {
                        return last_part.to_string();
                    }
                }
            }
        }
    }
    
    "unknown".to_string()
}

macro_rules! trace_call {
    ($fn_name:expr) => {
        let bt = Backtrace::new();
        let frames = bt.frames();
        
        let caller_fn = get_caller_name(&frames);
        
        let indent = {
            let mut level = INDENT_LEVEL.lock().unwrap();
            let current = *level;
            *level += 1;
            current
        };
        
        println!("{}→ Entering: {} (called from: {})", 
                 "  ".repeat(indent), 
                 $fn_name,
                 caller_fn);
    };
}

macro_rules! trace_exit {
    () => {
        let mut level = INDENT_LEVEL.lock().unwrap();
        if *level > 0 {
            *level -= 1;
        }
    };
}

fn function_a() {
    trace_call!("function_a");
    println!("    Executing function_a");
    function_b();
    trace_exit!();
}

fn function_b() {
    trace_call!("function_b");
    println!("    Executing function_b");
    function_c();
    function_d();
    trace_exit!();
}

fn function_c() {
    trace_call!("function_c");
    println!("    Executing function_c");
    trace_exit!();
}

fn function_d() {
    trace_call!("function_d");
    println!("    Executing function_d");
    function_e();
    trace_exit!();
}

fn function_e() {
    trace_call!("function_e");
    println!("    Executing function_e");
    trace_exit!();
}

fn recursive_function(depth: u32) {
    trace_call!("recursive_function");
    println!("    Recursive call depth: {}", depth);
    
    if depth > 0 {
        recursive_function(depth - 1);
    }
    
    trace_exit!();
}

fn main() {
    println!("=== Callstack Tracing Demo ===\n");
    
    println!("Test 1: Simple call chain");
    println!("--------------------------");
    function_a();
    
    println!("\nTest 2: Direct call from main");
    println!("--------------------------------");
    function_c();
    
    println!("\nTest 3: Recursive function");
    println!("----------------------------");
    recursive_function(3);
    
    println!("\n=== Demo Complete ===");
}
