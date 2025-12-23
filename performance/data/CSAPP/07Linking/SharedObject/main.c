#include <stdio.h>
#include <dlfcn.h>

void func()
{
    printf("func\n");
}

int main()
{
    void* pPlugin = dlopen("./plugin.so", RTLD_GLOBAL | RTLD_NOW);
    if (pPlugin)
    {
        void(*hello)();
        hello = dlsym(pPlugin, "hello");
        if (hello)
        {
            hello();
        }
    }
    else
    {
        printf("error in open plugin: %s\n", dlerror());
    }
    printf("end\n");
    return 0;
}
