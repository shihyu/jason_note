#include <stdio.h>

// 聲明外部函數
extern void public_function();
extern void old_function();

int main() {
    printf("=== Using Dynamic Library ===\n");

    public_function();
    old_function();

    return 0;
}