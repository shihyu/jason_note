use std::io::Cursor;

fn main() {
    let input = "./src/api.rs";
    let dest = "./src/api.go";
    let mut output = Vec::<u8>::new();

    let mut cbuilder = cbindgen::Builder::new()
        .with_language(cbindgen::Language::C)
        .with_src(&input)
        .with_header("// This file is generated. Please DO NOT edit this C part manually.")
        .generate()
        .expect("Unable to generate bindings")
        .write(Cursor::new(&mut output));

    let mut output = String::from_utf8(output).expect("Unable to convert to string");
    let mut go_content = format!(
        "package main\n\n/*\n{output}*/\nimport \"C\"\nimport (\n\"unsafe\"\n\"runtime\"\n)\n");
    go_content.push_str("func main() {}\n");

    std::fs::write(&dest, go_content).expect("Unable to write file");
    std::process::Command::new("go")
                .arg("fmt")
                .arg(&dest)
                .status()
                .unwrap();
}
