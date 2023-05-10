/*
fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>())
}
*/
fn main() {
    //不同类型变量
    let z: u8 = 1;     // 声明u8类型的变量z，等同于let z = 1;
    let w: i32 = 3;    // 声明i32类型
    let x = 2.0;       // f64, 浮点数默认f64
    let y: f32 = 3.0;  // f32, 指定f32类型
    println!("numbers: {}, {}, {}, {}", w,x,y,z);

    //数值运算
    let sum = 5 + 10;             // 加法
    let difference = 95.5 - 4.3;  // 减法
    let product = 4 * 30;         // 乘法
    let quotient = 56.7 / 32.0;   // 除法
    let floored = 2 / 3;          // 结果为 0
    let remainder = 43 % 5;       // 取余
    println!("number ops: {}, {}, {}, {}, {}, {}",
        sum,difference,
        product,quotient,
        floored,remainder);
    //布尔和字符型
    let logic_check: bool = true;
    let c = 'z';
    println!("bool: {}, char: {}", logic_check, c);

    //整型形式
    //1. 可以用"_"连接，方便阅读
    //2. 可以在数字末尾加类型
    let dec0 = 1222;
    let dec1 = 12_22;
    let dec2 = 1_222;
    let dec3 = 1222u32;
    println!("dec = {}, {}, {}, {}", dec0,dec1,dec2,dec3);

    let hex = 0xff;             //十六进制
    let oct = 0o10;             //八进制
    let bin = 0b0000_0011;      //二进制
    println!("hex = {}, oct = {}, bin = {}", hex, oct, bin);
    

    //元组(tuple)
    //多类型的值组合成一个复合类型的主要方式; 元组长度固定
    let tup = (500, 6.4, 'L');
    println!("1st is {}", tup.0);
    println!("2nd is {}", tup.1);
    println!("3rd is: {}", tup.2);
    let (x, y, z) = tup;
    println!("x={}, y={}, z={}",x,y,z);

    //数组(array)
    //每个元素的类型必须相同; 长度固定
    let a = ["first", "second", "third", "fourth"]; //数组包含4个字符串
    let b: [u32; 5] = [1, 2, 3, 4, 5];              //数组包含5个i32类型的数
    let c = [3; 5];                                 //[3,3,3,3,3]
    println!("a[1]={}", a[1]);
    println!("array b, 1st={}, 2nd={}, 3rd={}, 4th={}, 5th={}", b[0],b[1],b[2],b[3],b[4]);
    println!("c[0]={}", c[0]);

}
