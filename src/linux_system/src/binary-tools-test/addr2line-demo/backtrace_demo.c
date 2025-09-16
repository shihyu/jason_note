#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <execinfo.h>
#include <signal.h>
#include <unistd.h>

#define BACKTRACE_SIZE 100

// 信號處理函數，捕獲段錯誤並打印調用棧
void signal_handler(int sig) {
    void *buffer[BACKTRACE_SIZE];
    int nptrs;

    printf("\n=== Caught signal %d ===\n", sig);

    // 獲取調用棧
    nptrs = backtrace(buffer, BACKTRACE_SIZE);
    printf("Backtrace returned %d addresses:\n", nptrs);

    // 打印原始地址（供 addr2line 使用）
    printf("\nRaw addresses for addr2line:\n");
    for (int i = 0; i < nptrs; i++) {
        printf("%p\n", buffer[i]);
    }

    // 也可以使用 backtrace_symbols 打印符號信息
    printf("\nBacktrace symbols:\n");
    char **strings = backtrace_symbols(buffer, nptrs);
    if (strings != NULL) {
        for (int i = 0; i < nptrs; i++) {
            printf("%s\n", strings[i]);
        }
        free(strings);
    }

    // 生成 addr2line 命令
    printf("\n=== addr2line commands to decode addresses ===\n");
    char exe_path[1024];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path)-1);
    if (len != -1) {
        exe_path[len] = '\0';
        printf("# Run these commands to decode addresses:\n");
        for (int i = 0; i < nptrs; i++) {
            printf("addr2line -Cfpe %s %p\n", exe_path, buffer[i]);
        }
    }

    exit(1);
}

// 測試函數鏈
void deep_function_4() {
    // 故意觸發段錯誤
    int *ptr = NULL;
    *ptr = 42;  // Line 50 - Segfault here
}

void deep_function_3() {
    printf("In deep_function_3\n");
    deep_function_4();
}

void deep_function_2() {
    printf("In deep_function_2\n");
    deep_function_3();
}

void deep_function_1() {
    printf("In deep_function_1\n");
    deep_function_2();
}

// 手動打印調用棧
void print_backtrace() {
    void *buffer[BACKTRACE_SIZE];
    int nptrs;

    nptrs = backtrace(buffer, BACKTRACE_SIZE);
    printf("\n=== Manual Backtrace (%d frames) ===\n", nptrs);

    for (int i = 0; i < nptrs; i++) {
        printf("Frame %d: %p\n", i, buffer[i]);
    }

    // 生成批量 addr2line 命令
    char exe_path[1024];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path)-1);
    if (len != -1) {
        exe_path[len] = '\0';
        printf("\n# Batch addr2line command:\naddr2line -Cfpe %s", exe_path);
        for (int i = 0; i < nptrs; i++) {
            printf(" %p", buffer[i]);
        }
        printf("\n");
    }
}

int main(int argc, char *argv[]) {
    printf("=== Backtrace Demo for addr2line ===\n");

    // 註冊信號處理器
    signal(SIGSEGV, signal_handler);
    signal(SIGABRT, signal_handler);

    if (argc > 1) {
        if (argv[1][0] == '1') {
            printf("Mode 1: Manual backtrace\n");
            print_backtrace();
        } else if (argv[1][0] == '2') {
            printf("Mode 2: Triggering segfault with backtrace\n");
            deep_function_1();
        }
    } else {
        printf("Usage: %s <mode>\n", argv[0]);
        printf("  1 - Print manual backtrace\n");
        printf("  2 - Trigger segfault with backtrace\n");
        printf("\nExample addresses from current run:\n");
        printf("  main:             %p\n", (void*)main);
        printf("  deep_function_1:  %p\n", (void*)deep_function_1);
        printf("  signal_handler:   %p\n", (void*)signal_handler);
    }

    return 0;
}