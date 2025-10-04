use std::ffi::CStr;
use std::os::raw::c_char;

extern "C" {
    fn HelloWorld() -> *const c_char;
}

pub fn hello_world() {
    let result = unsafe {
        HelloWorld()
    };
    let c_str = unsafe { CStr::from_ptr(result) };
    let string = c_str.to_str().expect("Error translating SQIP from library");
    println!("{}", string);
}


fn main() {
    println!("Hello, world!");
    hello_world();
}
