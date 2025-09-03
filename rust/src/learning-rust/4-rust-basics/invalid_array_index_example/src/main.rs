use rand::Rng;

//数组越界访问实验
fn main() {
    let test_array = [1, 2, 3];

    //访问超出数组范围的元素，编译会出错
    //println!("test_array[7]={}", test_array[7]);

    //生成1-10的随机整数
    let rand_number = rand::thread_rng().gen_range(1..11);
    //编译成功，运行时越界
    println!("test_array rand element={}", test_array[rand_number]);
}
