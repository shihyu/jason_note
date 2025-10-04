use hello_macro::HelloMacro;
use hello_macro_derive::HelloMacro;

struct Tiger;
impl HelloMacro for Tiger {
    fn hello_macro() {
        println!("Hello, Macro! I'm a tiger!");
    }
}

struct Lion;
impl HelloMacro for Lion {
    fn hello_macro() {
        println!("Hello, Macro! I'm a lion!");
    }
}

#[derive(HelloMacro)]
struct Dog;

fn main() {
    println!("Hello, world!");
    Tiger::hello_macro();
    Dog::hello_macro();
}

