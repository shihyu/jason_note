use std::fmt::Debug;

struct Calculator;

impl Calculator {
    fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }

    fn multiply(&self, a: i32, b: i32) -> i32 {
        a * b
    }
}

fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

fn process_data() {
    let calc = Calculator;
    let result = calc.add(5, 3);
    println!("Add result: {}", result);

    let result = calc.multiply(4, 7);
    println!("Multiply result: {}", result);
}

fn main() {
    println!("Program started");

    process_data();

    let fib = fibonacci(5);
    println!("Fibonacci(5) = {}", fib);
}