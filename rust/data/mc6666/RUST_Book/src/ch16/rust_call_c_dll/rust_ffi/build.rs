use cmake::Config;
use std::path::Path;

fn main() {
    let dst = Config::new(Path::new("..").join("c_cpp")).build();

    println!("cargo:rustc-link-search=native={}", dst.display());
    println!("cargo:rustc-link-lib=dylib=c_cpp");
}
