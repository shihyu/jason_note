.intel_syntax noprefix
jmp start
msg: .ascii "Hello from shellcode\n"
start:
lea rsi, [rip - 28]
mov rax, 1
mov rdi, 1
mov rdx, 21
syscall
mov rax, 60
mov rdi, 0
syscall
