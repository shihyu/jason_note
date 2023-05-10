
fn main() {
    const ARRAY_MAX_NUM: usize = 1*1024*1024 +
        1021*1024 + 546;

    let array = [1; ARRAY_MAX_NUM];
    let size_of_element = std::mem::size_of_val(&array[0]);

    println!("sizeof one element = {} byte", size_of_element);
    println!("sizeof stack = {} bytes", size_of_element * ARRAY_MAX_NUM);
}

