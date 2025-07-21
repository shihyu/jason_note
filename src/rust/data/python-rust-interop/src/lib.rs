use pyo3::prelude::*;

#[pyfunction]
fn add_numbers(a: i32, b: i32) -> PyResult<i32> {
    Ok(a + b)
}

#[pyfunction]
fn multiply_numbers(a: f64, b: f64) -> PyResult<f64> {
    Ok(a * b)
}

#[pyfunction]
fn process_string(text: String) -> PyResult<String> {
    Ok(format!("Processed by Rust: {}", text.to_uppercase()))
}

#[pyfunction]
fn fibonacci(n: u32) -> PyResult<u64> {
    fn fib(n: u32) -> u64 {
        match n {
            0 => 0,
            1 => 1,
            _ => fib(n - 1) + fib(n - 2),
        }
    }
    Ok(fib(n))
}

#[pymodule]
fn rust_python_example(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(add_numbers, m)?)?;
    m.add_function(wrap_pyfunction!(multiply_numbers, m)?)?;
    m.add_function(wrap_pyfunction!(process_string, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci, m)?)?;
    Ok(())
}