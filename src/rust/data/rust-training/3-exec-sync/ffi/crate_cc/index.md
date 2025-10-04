藉助 cc crate可以完成Rust中嵌入的C代碼的編譯和鏈接。

1、添加對cc crate 的build依賴
```toml
[build-dependencies]
cc="1.0.53" #自動構建編譯C/C++代碼
```

2、在build.rs文件中添加cc的構建邏輯

```rust
//build.rs
fn main(){
    //the cc crate專門自動構建編譯C/C++ code,
    //如:自動檢測:系統平臺， 硬件架構， 自動選擇相應編譯器，設定各種編譯參數，
    //自動設定相關環境變量， 如:cargo相關環境變量， 自動將編譯好的C庫保存到“OUT_DIR”
    //所以cc可以自動幫你搞定諸如:交叉編譯， 跨平臺。
    //cargo build ‐vv 可以看到已經自動設定的各種構建參數。
    //詳情請參考:`https://docs.rs/cc/1.0.53/cc/`
    cc::Build::new()
    .file("src/hello.c")
    .compile("hello");
    println!("cargo:rerun‐if‐changed=src/hello.c"); //告訴cargo 只有當src/hello.c發生變 化時，才重新執行build.rs腳本。
}
```

3、在hello.c文件中添加C代碼
```
#include <stdio.h>
void hello(){
    printf("Hello, World!\n");
}
```

4、在rust中對C代碼進行調用
在 rust中，不需要使用#[link]屬性指定需要鏈接的C庫。
Cargo會依賴在build.rs構建腳本進行自動鏈接。

```
extern "C" { fn hello(); }
fn main(){
    unsafe { hello(); }
}
```

5、cargo run即可
在 Linux 下編譯運行（Mac上會有報錯）
```go
#cargo run
Hello, World!
```

## 參考
- [Build Script Examples](https://doc.rust-lang.org/cargo/reference/build-script-examples.html)
- [pkg_config工具](https://docs.rs/pkg-config/0.3.17/pkg_config/)