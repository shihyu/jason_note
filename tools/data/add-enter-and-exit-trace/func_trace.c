#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

#define PATH_MAX 250
static char path[PATH_MAX];

void
__attribute__((constructor))
trace_begin(void)
{
    readlink("/proc/self/exe", path, PATH_MAX);
}


#ifdef __cplusplus
extern "C" {
#endif

void end_str(char* str)
{
    unsigned int i;

    for (i = 0; i < PATH_MAX; ++i)
        if (str[i] == '\n') {
            str[i] = '\0';
        }
}

__attribute__((no_instrument_function))
void __cyg_profile_func_enter(void* this_fn, void* call_site)
{
    char buf[PATH_MAX];
    char cmd[PATH_MAX];

    memset(buf, 0, sizeof(buf));
    memset(cmd, 0, sizeof(cmd));

    snprintf(cmd, PATH_MAX, "addr2line -f -s -e \"%s\" %p", path, this_fn);
    printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        end_str(buf);
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

    snprintf(cmd, PATH_MAX, "addr2line -f -s -e \"%s\" %p", path, this_fn);
    // printf("\n%s\n", cmd);

    FILE* ptr = NULL;
    memset(buf, 0, sizeof(buf));

    if ((ptr = popen(cmd, "r")) != NULL) {
        fgets(buf, PATH_MAX, ptr);
        end_str(buf);
        printf("exit func <= %p:%s\n", this_fn, buf);
    }

    (void) pclose(ptr);
}
#ifdef __cplusplus
}
#endif

