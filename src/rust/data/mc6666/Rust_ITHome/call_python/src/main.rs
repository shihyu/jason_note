use pyo3::prelude::*;
use pyo3::types::PyTuple;
// use std::ffi::CString;
// use pyo3::ffi::c_str;

fn test1() -> PyResult<()> {
    let arg1 = "arg1";
    let arg2 = "arg2";
    let arg3 = "arg3";

    Python::with_gil(|py| {
        // Deprecated since 0.23.0: renamed to PyModule::from_code
        let fun: Py<PyAny> = PyModule::from_code_bound(
            py,
            "def example(*args, **kwargs):
                if args != ():
                    print('called with args', args)
                if kwargs != {}:
                    print('called with kwargs', kwargs)
                if args == () and kwargs == {}:
                    print('called with no arguments')",
            "",
            "",
        )?
        .getattr("example")?
        .into();

        // call object without any arguments
        fun.call0(py)?;

        // pass object with Rust tuple of positional arguments
        let args = (arg1, arg2, arg3);
        fun.call1(py, args)?;

        // call object with Python tuple of positional arguments
        let args = PyTuple::new_bound(py, &[arg1, arg2, arg3]);
        fun.call1(py, args)?;
        Ok(())
    })
}

fn main() {
    let _ = test1();

    let code = std::fs::read_to_string("example.py").unwrap();
    let _ = Python::with_gil(|py| -> PyResult<()> {
        PyModule::from_code_bound(py, &code, "example.py", "example")?;
        Ok(())
    });
}
