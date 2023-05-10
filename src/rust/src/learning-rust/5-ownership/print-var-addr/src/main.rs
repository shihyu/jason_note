fn main() {
    let s = String::from("hello");

    //打印s的地址，s本身在栈上，存了指针指向数据'hello'。
    println!("addr of s={:p} on stack", &s);

    //打印s指向的字符串'hello'在堆上的地址
    println!("addr of data 'hello'={:p} on heap", s.as_ptr());

    let x = 5;
    //x和值5都在栈上
    println!("x={}", x);
    println!("addr of x={:p}", &x);
}


