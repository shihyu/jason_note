#!/usr/bin/env python3

import rust_python_example

def main():
    print("=== Python calling Rust functions ===")
    
    # Test integer addition
    result1 = rust_python_example.add_numbers(10, 20)
    print(f"add_numbers(10, 20) = {result1}")
    
    # Test float multiplication
    result2 = rust_python_example.multiply_numbers(3.14, 2.0)
    print(f"multiply_numbers(3.14, 2.0) = {result2}")
    
    # Test string processing
    result3 = rust_python_example.process_string("hello world")
    print(f"process_string('hello world') = {result3}")
    
    # Test fibonacci calculation
    result4 = rust_python_example.fibonacci(10)
    print(f"fibonacci(10) = {result4}")
    
    print("\n=== Performance comparison ===")
    import time
    
    # Rust fibonacci
    start = time.time()
    rust_fib = rust_python_example.fibonacci(35)
    rust_time = time.time() - start
    print(f"Rust fibonacci(35) = {rust_fib}, time: {rust_time:.4f}s")
    
    # Python fibonacci for comparison
    def python_fibonacci(n):
        if n <= 1:
            return n
        return python_fibonacci(n-1) + python_fibonacci(n-2)
    
    start = time.time()
    python_fib = python_fibonacci(35)
    python_time = time.time() - start
    print(f"Python fibonacci(35) = {python_fib}, time: {python_time:.4f}s")
    
    if rust_time > 0:
        speedup = python_time / rust_time
        print(f"Rust is {speedup:.1f}x faster than Python")

if __name__ == "__main__":
    main()