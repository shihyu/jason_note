#include <cxxabi.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#define PATH_MAX 1024
#define gettid() syscall(SYS_gettid)
#define DUMP(func, call) printf("%s: func = %p, called by = %p/n", __FUNCTION__, func, call)

static char path[PATH_MAX];

void end_str(char* str)
{
    unsigned int i;

    for (i = 0; i < PATH_MAX; ++i)
        if (str[i] == '\n') {
            str[i] = '\0';
        }
}


void
__attribute__((constructor))
trace_begin(void)
{
    // printf("%s\n", path);
    readlink("/proc/self/exe", path, PATH_MAX);
}

// __attribute__((constructor))
// static void executable_path_init()
// {
//     char    buf[PATH_MAX];
//
//     memset(buf, 0, sizeof(buf));
//     memset(path, 0, sizeof(path));
//
// #ifdef _SOLARIS_TRACE
//     getcwd(buf, PATH_MAX);
//     sprintf(path, "%s/%s", buf, getexecname());
// #elif _LINUX_TRACE
//     readlink("/proc/self/exe", path, PATH_MAX);
// #else
// #endif
// }

#ifdef __cplusplus
extern "C" {
#endif
__attribute__((no_instrument_function))
void __cyg_profile_func_enter(void* this_fn, void* call_site)
{
    char buf[PATH_MAX];
    char cmd[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(cmd, 0, sizeof(cmd));

    // sprintf(cmd, "addr2line %p -e %s -f|head -1", this_fn, path);
    snprintf(cmd, PATH_MAX, "addr2line -f -s -e \"%s\" %p", path, this_fn);
    // printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        end_str(buf);
        // printf("enter func => %p:%s\n", this_fn, abi::__cxa_demangle(buf, nullptr, nullptr, nullptr) );
        printf("enter func => %p:%s\n", this_fn, buf);
    }

    (void) pclose(ptr);
}

__attribute__((no_instrument_function))
void __cyg_profile_func_exit(void* this_fn, void* call_site)
{
    char buf[PATH_MAX];
    char cmd[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(cmd, 0, sizeof(cmd));

    // sprintf(cmd, "addr2line %p -e %s -f|head -1", this_fn, path);
    snprintf(cmd, PATH_MAX, "addr2line -f -s -e \"%s\" %p", path, this_fn);
    // printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        end_str(buf);
        printf("exit func => %p:%s\n", this_fn, buf);
        // printf("exit func => %p:%s\n", this_fn, abi::__cxa_demangle(buf, nullptr, nullptr, nullptr) );
    }

    (void) pclose(ptr);
}
#ifdef __cplusplus
}
#endif

