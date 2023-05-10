#[allow(dead_code)]

//Debug输出格式, Debug是一个trait, derive增加派生Debug trait
#[derive(Debug)]

struct Rectangle {
    width: u32,
    height: u32,
}
fn main() {
    let rect1 = Rectangle {
        width: 50,
        height: 80
    };
//    println!("rect1 is {:#?}", rect1);
    dbg!(&rect1);
}




