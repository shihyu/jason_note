extern "C" { fn hello(); }

fn main(){
    unsafe { hello(); }
}
