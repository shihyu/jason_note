

## Go 動態鏈接庫
- import偽包C
- 用//export FunctionNameHere的註釋標記函數
- 編譯為動態鏈接庫
```shell
#go build -o libhello.dylib -buildmode=c-shared main.go
```

- 或者也可以編譯為靜態鏈接庫
```shell
#go build -o libhello.dylib -buildmode=c-archive main.go
```

## Rust引用 Go 動態鏈接庫
- 第一，在目的根目錄下添加一個build.rs文件。這將在構建過程中由Cargo調用。
```rust
fn main() {
    let path = "./lib";
    let lib = "hello";

    println!("cargo:rustc-link-search=native={}", path);
    println!("cargo:rustc-link-lib=dylib={}", lib);
}
```
或者也可以直接指定golang源碼

```rust
fn main() {
    rust2go::Builder::new().with_go_src("./go").build();
}
```


- 第二、extern塊列出了外部接口中所有的函數及其類型簽名
```rust
extern "C" {
    fn HelloWorld() -> *const c_char;
}
```

- 第三、在一個安全的簽名中包裝這個不安全的接口
```rust
pub fn hello_world() {
    let result = unsafe { 
        HelloWorld()
    };
    let c_str = unsafe { CStr::from_ptr(result) };
    let string = c_str.to_str().expect("Error translating SQIP from library");
    println!("{}", string);
}
```

## 編譯運行
編譯後，需要將動態鏈接庫文件拷貝到可執行文件同一目錄下，否則會找不到動態鏈接庫文件。
```
% cargo run
    Finished dev [unoptimized + debuginfo] target(s) in 0.03s
     Running `target/debug/rust2go`
Hello, world!
Hello, world, From GO!
```