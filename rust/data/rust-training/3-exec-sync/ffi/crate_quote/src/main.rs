use quote::{format_ident, quote, ToTokens};

fn main() {
    let mut generated_code = quote! {
        pub struct MyStruct {
            pub field1: i32,
            pub field2: String,
        }
    };

    generated_code.extend(quote! {
        fn add(x: i32, y: i32) -> i32 {
            x + y
        }
    });

    print!("{}", generated_code.to_string());
}

