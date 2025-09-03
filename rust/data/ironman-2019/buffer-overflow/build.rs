fn main() {
    cc::Build::new()
        .file("src/jump_stack.s")
        .compile("jump_stack");
}
