
fn scope_mem_example () {
    { // s 在这里无效, 它尚未声明

        //编译进程序里的字符串，不可变; 压入栈中，保存。
        let s = "hello";        // 从此处起，s 是有效的
        println!("s = {}",s);

    } // 此作用域已结束，s不再有效, 值被移出栈。

    //s无效，编译会出错
//    println!("print again, s = {}",s);
}

fn scope_mem_example2 () {
    {
        //s2大小可变，from()函数从堆上malloc分配内存，数据存在堆上。
        let mut s2 = String::from("hello");

        s2.push_str(", world!"); // push_str() 在字符串后加字符

        println!("{}", s2);
    } //这里自动调用drop函数释放s2在堆上的内存
}

fn heap_data_move() {
    let s1 = String::from("hello");
    println!("1st place, s1 = {}", s1);
    let s2 = s1;
    //s1, s2都指向保存'hello'的那块堆上的内存
    //为了防止double free，s2创建后，s1失效, s1移到了s2
    //C语言没有这个功能，有很多double free问题要debug

    //这里会编译出错
    //println!("2nd place, s1 = {}", s1);
}

fn heap_data_clone() {
    let s1 = String::from("hello");
    let s2 = s1.clone();
    println!("s1 = {}, s2 = {}", s1, s2);
}

fn stack_datatype_copy() {
    // x和y是独立的两个变量，都等于5，放到了栈上两个地址。
    let x = 5;
    let y = x;

    //x是i32类型，实现了Copy trait，作用类似于上面的clone。
    //任何不需要分配内存或某种形式资源的类型都可以实现Copy，
    //如标量类型和其组合都实现了Copy trait
    //所有整数, 布尔, 浮点, 字符类型。 
    println!("x={}, y={}",x,y);
}

fn main() {
//    scope_mem_example();
//    scope_mem_example2();
//    heap_data_move();
//    heap_data_clone();

    stack_datatype_copy();
}







