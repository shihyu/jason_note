use std::{
    io::{self, Read},
    ptr,
};

extern "C" {
    pub fn jump_stack() -> !;
}

fn use_jump_stack() {
    println!("This should not print");
    unsafe {
        jump_stack();
    }
}

fn buffer_overflow(b: &[u8]) {
    let mut buf = [0u8; 0];
    unsafe {
        ptr::copy(b.as_ptr(), buf.as_mut_ptr(), b.len());
    }
}

fn main() {
    let mut buf = Vec::new();
    unsafe {
        libc::mprotect(
            (&mut buf as *mut _ as usize & (-libc::sysconf(libc::_SC_PAGE_SIZE) as usize))
                as *mut libc::c_void,
            4096,
            libc::PROT_READ | libc::PROT_WRITE | libc::PROT_EXEC,
        );
    }
    io::stdin().read_to_end(&mut buf).unwrap();
    buffer_overflow(&buf);
    use_jump_stack();
}
