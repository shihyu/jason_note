宏和函數最大的區別是宏是編譯時執行的，而函數是運行時執行的。

過程宏有三種形式:

- 類函數宏(function-like macros) - custom!(...)
- 派生宏(derive macros)- #[derive(CustomDerive)]
- 屬性宏(attribute macros) - #[CustomAttribute]


## derive宏
如果不使用derive過程宏，則需要為每個結構體實現一系列的函數。例如：

```rust
pub trait HelloMacro {
    fn hello_macro();
}
struct Tiger;
impl HelloMacro for Tiger {
    fn hello_macro() {
        println!("Hello, Macro! I'm a tiger!");
    }
}
```

而如果使用drive宏，就可以通過如下簡單方式為struct添加hello_macro功能：
```
use hello_macro_derive::HelloMacro;
#[derive(HelloMacro)]
struct Dog;
```

derive過程宏只能用在struct/enum/union上。 其定義方式如下：
```
#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // 基於 input 構建 AST 語法樹
    let ast:DeriveInput = syn::parse(input).unwrap();

    // 構建特徵實現代碼
    impl_hello_macro(&ast)
}

fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let gen = quote! {
        impl HelloMacro for #name {
            fn hello_macro() {
                println!("Hello, Macro! My name is {}!", stringify!(#name));
            }
        }
    };
    gen.into()
}
```

其中 syn::parse 函數將 TokenStream 轉換為 AST 語法樹，會返回一個 DeriveInput 結構體來代表解析後的 Rust 代碼。
對於 struct Dog 來說，DeriveInput 結構體的定義如下：
```go
DeriveInput {
    // --snip--
    vis: Visibility,
    ident: Ident {
        ident: "Dog",
        span: #0 bytes(95..103)
    },
    generics: Generics,
    // Data是一個枚舉，分別是DataStruct，DataEnum，DataUnion，這裡以 DataStruct 為例
    data: Data(
        DataStruct {
            struct_token: Struct,
            fields: Fields,
            semi_token: Some(
                Semi
            )
        }
    )
}
```

quote! 宏用於構建 TokenStream。



## 參考
- [Rust語言聖經](https://course.rs/advance/macro.html)