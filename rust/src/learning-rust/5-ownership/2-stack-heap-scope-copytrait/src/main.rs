fn main() {
    let s = String::from("hello");
    println!("s={}", s);
    //s本身保存在栈上
    //'hello'本身保存在堆上
    //s栈地址里面保存了地址，地址指向'hello'在堆上的地址
    println!("addr of data 'hello'={:p} on heap", s.as_ptr());
    println!("addr of s={:p} on stack", &s);
//    let s2 = s; //s所有权移到s2
//    println!("addr of s={:p} on stack", &s2);
    func1(s);   //s所有权移到函数里
    //s到这里不再有效
    //println!("after func1, s={}", s);

    println!("---------------------");
    let x = 10;
    println!("x={}", x);
    println!("addr of x={:p}", &x);
//    let y = x;
    func2(x);
    //x是i32类型，有Copy trait，所以在后面可继续使用x
    println!("after func2, x={}", x);
    println!("after func2, addr of x={:p}", &x);
}

fn func1(some_string: String) {
    println!("in func1, s={}", some_string);
    println!("in func1, addr of s={:p}", some_string.as_ptr());
} // some_string 移出作用域并调用 `drop` 方法。

fn func2(some_integer: i32) {
    println!("in func2, x={}", some_integer);
    println!("in func2, addr of x={:p}", &some_integer);
} // some_integer 移出作用域, 出栈

