使用 syn crate 可以實現對 rust 代碼的解析，也可以添加自定義的 derive 宏。

讀取並解析rust代碼

```rust
    let input = "./src/input.rs";
    let file_content = std::fs::read_to_string(&input).expect("Unable to read file");
    let syntax = syn::parse_file(&file_content).expect("Unable to parse file");
```

遍歷語法樹，並查看解析結果

```rust
   // 遍歷語法樹
    for item in syntax.items.iter() {
        match item {
            Item::Struct(s) => {
                let struct_name = s.ident.clone();
                let struct_name_ref = format_ident!("{}Ref", struct_name);
                let mut field_names = Vec::with_capacity(s.fields.len());
                for field in s.fields.iter() {
                    let field_name = field
                        .clone()
                        .ident;
                    field_names.push(field_name);
                }
                println!("{}", struct_name);
                println!("{}", struct_name_ref);
                println!("{:?}", field_names);
            }
            _ => continue,
        }
    }
```