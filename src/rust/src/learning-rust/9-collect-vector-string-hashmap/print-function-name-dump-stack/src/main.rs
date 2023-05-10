use stdext::function_name;
use backtrace::Backtrace;

fn dump_stack_test() {
    let bt = Backtrace::new();
    println!("backtrace dump start ===============");
    println!("{:?}", bt);
}

fn test_func() {
    println!("function name is={}",function_name!());
    dump_stack_test();
}

fn main() {
    println!("Current position: {}:{} - {}", file!(), line!(), module_path!());
    test_func();
}


