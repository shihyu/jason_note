#include <stdio.h>
#include <time.h>

// 使用 visibility 屬性控制導出
__attribute__((visibility("default")))
void public_function() {
    printf("This is a public function\n");
}

__attribute__((visibility("hidden")))
void private_function() {
    printf("This is a private function (hidden)\n");
}

// 構造和析構函數
__attribute__((constructor))
void lib_init() {
    printf("Library initialized at %ld\n", time(NULL));
}

__attribute__((destructor))
void lib_cleanup() {
    printf("Library cleanup\n");
}

// 版本化符號 - 簡化版本，不使用 symver
void old_function() {
    printf("Function implementation\n");
}

// 全局變量
int global_variable = 42;