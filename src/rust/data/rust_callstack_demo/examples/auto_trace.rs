use backtrace::{Backtrace, BacktraceFrame};
use std::sync::Mutex;

static INDENT_LEVEL: Mutex<usize> = Mutex::new(0);

fn extract_function_name(frames: &[BacktraceFrame], skip: usize) -> String {
    if let Some(frame) = frames.get(skip) {
        for symbol in frame.symbols() {
            if let Some(name) = symbol.name() {
                let full_name = name.to_string();
                let parts: Vec<&str> = full_name.split("::").collect();
                if let Some(&last) = parts.last() {
                    if last.starts_with("h") && last.len() == 17 && parts.len() >= 2 {
                        return parts[parts.len() - 2].to_string();
                    } else {
                        return last.to_string();
                    }
                }
            }
        }
    }
    "unknown".to_string()
}

macro_rules! auto_trace {
    () => {
        let bt = Backtrace::new();
        let frames = bt.frames();
        
        let current_fn = extract_function_name(&frames, 1);
        let caller_fn = extract_function_name(&frames, 2);
        
        let indent = {
            let mut level = INDENT_LEVEL.lock().unwrap();
            let current = *level;
            *level += 1;
            current
        };
        
        println!("{}→ {} called by {}", 
                 "  ".repeat(indent), 
                 current_fn,
                 caller_fn);
    };
}

macro_rules! trace_return {
    () => {
        let mut level = INDENT_LEVEL.lock().unwrap();
        if *level > 0 {
            *level -= 1;
        }
    };
}

fn calculate_factorial(n: u32) -> u32 {
    auto_trace!();
    
    let result = if n <= 1 {
        1
    } else {
        n * calculate_factorial(n - 1)
    };
    
    trace_return!();
    result
}

fn process_data(value: u32) {
    auto_trace!();
    println!("    Processing value: {}", value);
    
    let fact = calculate_factorial(value);
    println!("    Factorial of {} is {}", value, fact);
    
    trace_return!();
}

fn complex_workflow() {
    auto_trace!();
    
    validate_input();
    process_data(5);
    generate_output();
    
    trace_return!();
}

fn validate_input() {
    auto_trace!();
    println!("    Validating input...");
    trace_return!();
}

fn generate_output() {
    auto_trace!();
    println!("    Generating output...");
    format_result();
    trace_return!();
}

fn format_result() {
    auto_trace!();
    println!("    Formatting result...");
    trace_return!();
}

fn main() {
    println!("=== Automatic Callstack Tracing Demo ===\n");
    
    println!("Test 1: Complex workflow");
    println!("-------------------------");
    complex_workflow();
    
    println!("\nTest 2: Direct factorial calculation");
    println!("--------------------------------------");
    let result = calculate_factorial(4);
    println!("Result: {}", result);
    
    println!("\n=== Demo Complete ===");
}