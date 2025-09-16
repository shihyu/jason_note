#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// 故意製造段錯誤的函數
void cause_segfault() {
    char *ptr = NULL;
    printf("About to cause segfault...\n");
    // 訪問空指針導致段錯誤
    *ptr = 'x';  // Line 10 - 這裡會發生段錯誤
}

// 遞歸函數用於產生調用棧
void recursive_function(int depth) {
    if (depth > 0) {
        recursive_function(depth - 1);
    } else {
        cause_segfault();
    }
}

// 測試函數（不使用 inline 避免鏈接問題）
int test_function(int x) {
    return x * 2;
}

// 複雜的調用鏈
void function_c() {
    recursive_function(3);
}

void function_b() {
    function_c();
}

void function_a() {
    function_b();
}

int main(int argc, char *argv[]) {
    printf("=== addr2line Segfault Demo ===\n");
    printf("PID: %d\n", getpid());

    if (argc > 1 && strcmp(argv[1], "--crash") == 0) {
        printf("Triggering crash for addr2line demo...\n");
        function_a();
    } else {
        printf("Run with --crash to trigger segfault\n");
        printf("Example: %s --crash\n", argv[0]);

        // 顯示一些函數地址供測試
        printf("\nFunction addresses for testing:\n");
        printf("main:              %p\n", (void*)main);
        printf("function_a:        %p\n", (void*)function_a);
        printf("cause_segfault:    %p\n", (void*)cause_segfault);
        printf("test_function:     %p\n", (void*)test_function);
    }

    return 0;
}