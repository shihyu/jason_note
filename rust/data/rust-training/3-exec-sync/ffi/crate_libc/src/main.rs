fn main() {
    unsafe {
        let pid = libc::fork();

        if pid > 0 {
            println!("Hello, I am parent thread: {}", libc::getpid());
        }
        else if pid == 0 {
            println!("Hello, I am child thread: {}", libc::getpid());
            println!("My parent thread: {}", libc::getppid());
        }
        else {
            println!("Fork creation failed!");
        }
    }
}
