fn loop_label() {
    'first_loop: loop {
        println!("1-In outer loop");
        let mut count = 0;
        loop {
            println!("2-In inner loop");
            count += 1;
            /*
            if count%4 == 0 {
                println!("3-break inner loop");
                break;
            }
            */
            if count%4 == 0 {
                println!("3-break outter loop directly");
                break 'first_loop;
            }
        }
    }
    println!("4-end of function");
}

fn return_val_in_loop() {
    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;
        }
    };
    println!("return_val_in_loop() return, result = {}", result);
}

fn main() {
    loop_label();
    return_val_in_loop();
}







