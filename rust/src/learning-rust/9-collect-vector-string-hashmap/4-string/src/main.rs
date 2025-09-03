fn func1() {
    let s1 = String::from("tic");
    let s2 = String::from("tac");
    let s3 = String::from("toe");
    let s = format!("{}-{}-{}", s1, s2, s3);
    println!("func1, s={}", s);
}

fn func2() {
    let hello = "Здравствуйте";
    let s = &hello[0..4];
    //let s = &hello[0..1];
    println!("func2, s={}", s);
}
fn func3() {
    for c in " नमस◌्त◌े".chars() {
        println!("{}", c);
    }
    for b in " नमस◌्त◌े".bytes() {
        println!("{}", b);
    }
}
fn main() {
    let mut s1 = String::new();
    let mut s2 = "hello test_string2".to_string();
    let mut s3 = String::from("你好,");

    println!("s1={}, s2={}, s3={}",s1, s2, s3);

    s1.push_str("test_string1");
    s2.push('!');      //"!"->String, '!'->char
    s3 = s3 + "rust";
    println!("after update, s1={}, s2={}, s3={}",s1, s2, s3);

    func1();
    func2();
    func3();
}
