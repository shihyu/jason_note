fn func1() {
    let s = String::from("hello world");
    let hello = &s[0..5];
    let world = &s[6..11];
    println!("{}", hello);
    println!("{}", world);
}
/*
fn func2() {
    let s = String::from("hello world");
    let hello = &s[..5];
    let world = &s[6..];
    println!("{}", hello);
    println!("{}", world);
}

fn func3() {
    let s = String::from("hello world");
    let world = &s[3..100];
    println!("{}", world);
}

fn func4() {
    let s = String::from("hello world");
    let w = first_word(&s);
    println!("1st word = {}", w);
}
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}

fn func5() {
    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];
    println!("slice of array = {}, {}",slice[0], slice[1]);
}
*/

fn main() {
    func1();
}





