fn main() {
    ref1();
}

fn change(s1: &mut String) {
    s1.push_str(", rust");
}

fn ref1() {
    let mut s = String::from("hello");
    println!("s={}",s);
    change(&mut s);
    println!("after change, s={}", s);
}

/*
fn ref2() {
    let mut s = String::from("hello");
    let r1 = &mut s;
    //同一时间只能有一个对某一特定数据的可变引用，否则编译时会出错。
    //下面会编译出错
//    let r2 = &mut s;
//    println!("{}, {}", r1, r2);

    change(r1);
    println!("after change, {}", s);
}

fn ref3() {
    let mut s = String::from("hello");
    let r1 = &s; // 没问题
    let r2 = &s; // 没问题
    let r3 = &mut s; // 大问题
    println!("{}, {}, and {}", r1, r2, r3);
}

fn ref4() {
    let mut s = String::from("hello");
    let r1 = &s; // 没问题
    let r2 = &s; // 没问题
    println!("{} and {}", r1, r2);
    // 此位置之后 r1 和 r2 不再使用
    let r3 = &mut s; // 没问题
    change(r3);
    println!("{}", r3);
}
*/



