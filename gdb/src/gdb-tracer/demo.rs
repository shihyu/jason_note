// demo.rs - Simple Rust program to demonstrate tracing

fn main() {
    println!("Starting Rust demo");

    let x = 10;
    let y = 20;
    let result = calculate(x, y);

    println!("Result: {}", result);

    // Test with different types
    let text = process_string("Hello, Rust!");
    println!("Processed: {}", text);

    // Test with struct
    let data = DataStruct::new(42, "test");
    data.display();
}

fn calculate(a: i32, b: i32) -> i32 {
    let sum = add(a, b);
    let product = multiply(a, b);
    sum + product
}

fn add(x: i32, y: i32) -> i32 {
    x + y
}

fn multiply(x: i32, y: i32) -> i32 {
    x * y
}

fn process_string(input: &str) -> String {
    let upper = to_uppercase(input);
    add_suffix(&upper, "!!!")
}

fn to_uppercase(s: &str) -> String {
    s.to_uppercase()
}

fn add_suffix(s: &str, suffix: &str) -> String {
    format!("{}{}", s, suffix)
}

struct DataStruct {
    value: i32,
    name: String,
}

impl DataStruct {
    fn new(value: i32, name: &str) -> Self {
        DataStruct {
            value,
            name: name.to_string(),
        }
    }

    fn display(&self) {
        println!("DataStruct {{ value: {}, name: {} }}", self.value, self.name);
        self.internal_method();
    }

    fn internal_method(&self) {
        println!("Internal method called with value: {}", self.value);
    }
}