#include <unistd.h>

char* s = "yes\n";

int main()
{
    syscall(1, STDOUT_FILENO, "hello\n", 6);
    write(STDOUT_FILENO, "world\n", 6);
    // GCC inline assembly
    __asm__(
        "movq $1, %rax\n\t" // syscall number: 1
        "movq $1, %rdi\n\t" // STDOUT_FILENO is 1
        "movq s, %rsi\n\t" // value of s
        "movq $4, %rdx\n\t" // size: 4
        "syscall"
    );
    write(STDOUT_FILENO, "no\n", 3);
    return 0;
}