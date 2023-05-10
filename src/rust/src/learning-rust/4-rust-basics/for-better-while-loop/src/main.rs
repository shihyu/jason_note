fn while_loop() {
    let array = [1, 2, 3, 4, 5];
    let mut index = 0;
    println!("start of while");
    while index < 5 {
        println!("the value is: {}", array[index]);
        index += 1;
    }
}
fn loop_loop() {
    let array = [1, 2, 3, 4, 5];
    let mut index = 0;
    println!("start of loop");
    loop {
        if index == 5 {
            break;
        }
        println!("the value is: {}", array[index]);
        index += 1;
    }
}
fn for_loop() {
    let array = [1, 2, 3, 4, 5];

    println!("start of for");
    for x in array {
        println!("the value is: {}", x);
    }
}

fn main() {
    for_loop();
    while_loop();
    loop_loop();
}
