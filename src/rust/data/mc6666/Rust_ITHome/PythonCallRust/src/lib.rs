use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn factorial(a: i32) -> PyResult<i32> {
    let mut sum1:i32 = 1;
    for i in 1..(a+1) {
        sum1 = sum1 * i;
    }
    Ok(sum1)
}

/// A Python module implemented in Rust.
#[pymodule]
fn test1(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(factorial, m)?)?;
    Ok(())
}