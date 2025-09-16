#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>

void test_dlopen_flags() {
    void *handle;

    // RTLD_NOLOAD - 檢查庫是否已加載
    handle = dlopen("libc.so.6", RTLD_NOLOAD);
    if (handle) {
        printf("libc.so.6 is already loaded\n");
        dlclose(handle);
    }

    // Test dladdr
    Dl_info info;
    void *addr = (void *)printf;

    if (dladdr(addr, &info)) {
        printf("Function: %s\n", info.dli_sname);
        printf("Library: %s\n", info.dli_fname);
    }
}

int main() {
    test_dlopen_flags();
    return 0;
}
