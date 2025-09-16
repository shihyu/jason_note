#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

int main() {
    void *handle;
    void (*func)();
    char *error;

    // 打開動態庫
    handle = dlopen("./libdynamic.so", RTLD_LAZY);
    if (!handle) {
        fprintf(stderr, "dlopen error: %s\n", dlerror());
        return 1;
    }

    // 清除錯誤
    dlerror();

    // 獲取函數指針
    func = (void (*)()) dlsym(handle, "public_function");
    error = dlerror();
    if (error) {
        fprintf(stderr, "dlsym error: %s\n", error);
        dlclose(handle);
        return 1;
    }

    // 調用函數
    printf("Calling function from dynamically loaded library:\n");
    func();

    // 獲取變量地址
    int *var = (int *)dlsym(handle, "global_variable");
    if (var) {
        printf("Global variable value: %d\n", *var);
    }

    // 關閉庫
    dlclose(handle);

    return 0;
}