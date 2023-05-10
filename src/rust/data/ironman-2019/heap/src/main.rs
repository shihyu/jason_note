mod utils;
mod v1;

#[global_allocator]
static ALLOC: v1::MyAlloc = v1::MyAlloc::new();

fn main() {
    println!("{}", "Hello world".to_owned());
}
