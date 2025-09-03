#[derive(Debug)]

struct Rectangle {
    width: u32,
    height: u32,
}
//implementation
impl Rectangle {
    //方法的第一个参数必须为self的Self类型参数
    fn area(&self) -> u32 {
        self.width * self.height
    }
    fn can_hold(&self, other:&Rectangle) -> bool {
        self.width>other.width && self.height>other.height
    }
}
//每个结构体都允许拥有多个impl块
impl Rectangle {
    //关联函数，不是方法(第一个参数不是self)
    fn square(size: u32) -> Rectangle {
        Rectangle {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    let rect2 = Rectangle {
        width: 20,
        height: 30,
    };
    println!("area = {}", rect1.area());
    println!("rect1 can hold rect2? -> {}", rect1.can_hold(&rect2));

    let sq = Rectangle::square(3);
    dbg!(&sq);
}











