#ifdef RUNTIME
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

// wrapper
void* malloc(size_t size)
{
    void* (*mallocp)(size_t size);
    mallocp = dlsym(RTLD_NEXT, "malloc"); // get malloc in libc.so
    if (!mallocp)
    {
        printf(dlerror());
        exit(1);
    }
    char* ptr = mallocp(size);
    printf("malloc(%d) = %p\n", size, ptr);
    return ptr;
}
void free(void* ptr)
{
    void (*freep)(void*) = NULL;
    if (!ptr)
        return;
    freep = dlsym(RTLD_NEXT, "free"); // get free in libc.so
    if (!freep)
    {
        printf(dlerror());
        exit(1);
    }
    free(ptr);
    printf("free(%p)\n", ptr);
}
#endif