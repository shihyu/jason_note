#define _GNU_SOURCE
#include <stdio.h>
#include <dlfcn.h>

int main() {
    void *handle;

    // Test RTLD_NOLOAD - check if library is loaded
    printf("Testing RTLD_NOLOAD:\n");
    handle = dlopen("libc.so.6", RTLD_NOLOAD);
    if (handle) {
        printf("  libc.so.6 is already loaded\n");
        dlclose(handle);
    } else {
        printf("  libc.so.6 is not loaded\n");
    }

    // Test loading math library
    printf("\nTesting dlopen with libm:\n");
    handle = dlopen("libm.so.6", RTLD_LAZY);
    if (handle) {
        printf("  Successfully loaded libm.so.6\n");

        // Get sqrt function
        double (*sqrt_fn)(double) = dlsym(handle, "sqrt");
        if (sqrt_fn) {
            printf("  sqrt(144) = %.2f\n", sqrt_fn(144));
        }

        dlclose(handle);
    }

    return 0;
}