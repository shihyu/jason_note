fn main() {
    // 告訴 cargo 在哪裡尋找 C 函式庫
    println!("cargo:rustc-link-search=native=../../c_libs");
    println!("cargo:rustc-link-lib=math");
    
    // 當 C 函式庫改變時重新編譯
    println!("cargo:rerun-if-changed=../../c_libs/libmath.so");
}