use stdext::function_name;
fn add_elem() {
    println!("{}",function_name!());

    let mut v1: Vec<i32> = Vec::new();
    println!("add_elem: vector1={:?}", v1);
    v1.push(10);
    v1.push(20);
    v1.push(30);
    println!("add_elem: vector1={:?}", v1);
}

fn get_elem() {
    let v2 = vec![1,2,3];

    let num = &v2[1];
    println!("get_elem: elem in v2 is {}", num);

    let num2 = v2.get(1);
    match num2 {
        Some(n) => println!("get_elem: elem in v2 is {}",n),
        None => ()
    }
}

fn owner_change() {
    let v = vec![4,5,6];
    let v2 = &v;
    println!("owner_change: vector={:?}", v);
    println!("owner_change: vector2={:?}", v2);
}

fn print_vec(v: &Vec<i32>) {
    for i in v {
        println!("{}",i);
    }
}
fn loop_vec() {
    let mut v = vec![7,8,9];
    print_vec(&v);
    for i in &mut v {
        *i += 10;
    }
    print_vec(&v);

}

fn main() {
    add_elem();
    get_elem();
    owner_change();
    loop_vec();
}











