//整数溢出实验

fn main() {
    //编译出错
    //let mut big_num: u32 = 4294967296;

    let mut big_num: u32 = 4294967295;
    println!("current num = {}", big_num);

    //下面编译正常，运行时导致整数溢出
    big_num = big_num + 1;
    println!("after added rand num, current num = {}", big_num);
}
