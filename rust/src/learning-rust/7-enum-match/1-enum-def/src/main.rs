#[derive(Debug)]
//没有存实际IP地址数据, 只知道它是什么类型的
enum IpAddrKind {
    V4,
    V6,
}

//每一个枚举成员的名字也变成了一个函数
//IpAddr::V4()是一个获取String参数并返回IpAddr类型实例的函数调用
//这些构造函数会自动被定义。
#[derive(Debug)]
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}

fn func1()
{
    let f = IpAddrKind::V4;
    let s = IpAddrKind::V6;
    println!("ip v4 f={:#?}",f);
    println!("ip v6 s={:#?}",s);

    let home_ip = IpAddr::V4(127,0,0,1);
    let home_ipv6 = IpAddr::V6(String::from("::1"));
    dbg!(&home_ip);
    dbg!(&home_ipv6);
}
////////////////////////////////////////////////////////
#[derive(Debug)]
//可以定义多个不同类型数据
enum Message {
    Quit,
    Write(String),
    ChangeColor(i32, i32, i32),
}
/* 和结构体类似
struct Quit; // 类单元结构体
struct Write(String); // 元组结构体
struct ChangeColor(i32, i32, i32); // 元组结构体
*/
//定义方法，和结构体类似
impl Message {
    fn call(&self) {
        dbg!(&self);
    }
}
fn func2(){
    let q = Message::Quit;
    let w = Message::Write(String::from("test"));
    let c = Message::ChangeColor(1, 1, 1);
    dbg!(&q);
    dbg!(&w);
    dbg!(&c);

    let m = Message::Write(String::from("hello"));
    m.call();
}
///////////////////////////////////////////////////
fn main() {
    func1();
    func2();
}







