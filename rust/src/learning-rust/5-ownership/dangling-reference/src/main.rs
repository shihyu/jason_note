fn main() {
    dangle_right2();
}

/*
fn dangle_wrong1() {
    let s = String::from("hello");
    println!("s={}",s);
    let r1 = &s;
    let r2 = &s;

    let s2 = s;

    println!("{} {} {}",r1, r2, s2);
}

fn dangle_wrong2() -> &String { // dangle 返回一个字符串的引用
    let s = String::from("hello");
    &s // 返回字符串 s 的引用
} // 这里 s 离开作用域并被丢弃。其内存被释放。
*/

fn dangle_right2() -> String {
    let s = String::from("hello");
    s
    //所有权被移动出去，所以没有值被释放。
}





