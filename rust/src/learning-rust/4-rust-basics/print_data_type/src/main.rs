
fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>())
}

fn main() {
    let x: u32 = 1;

    print_type_of(&x);

}

