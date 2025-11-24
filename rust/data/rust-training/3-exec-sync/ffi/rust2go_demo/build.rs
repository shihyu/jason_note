fn main() {
    let path = "./lib";
    let lib = "hello";

    println!("cargo:rustc-link-search=native={}", path);
    println!("cargo:rustc-link-lib=dylib={}", lib);
}