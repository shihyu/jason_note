#[allow(dead_code)]
#[allow(unused_variables)]
fn func1() {
    let some_num = Some(5);             //some_num Option<i32>
    let some_str = Some("test string"); //Option<&str>
    let absent_num: Option<i32> = None;
}

#[allow(dead_code)]
#[allow(unused_variables)]
fn func2() {
    let num1 = Some(5);     //Option<i32>
    let num2: i32 = 3;      //i32
    //i32和Option类不能直接运算，下面编译出错
//    println!("sum = {} ", num1 + num2);

    //Option类型转换为i32再运算
    println!("sum = {} ", num1.unwrap() + num2);
}

fn main() {
    func2();
}

