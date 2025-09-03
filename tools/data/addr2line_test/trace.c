#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define STRMAX 90

static char exe[STRMAX], cmd[STRMAX];
static char func_name[STRMAX], caller_name[STRMAX], caller_file[STRMAX];

void end_str(char* str)
{
    unsigned int i;

    for (i = 0; i < STRMAX; ++i)
        if (str[i] == '\n') {
            str[i] = '\0';
        }
}

void get_addr(void* func, void* caller)
{
    /*
        printf("#DEBUG: func = %p\n", func);
        printf("#DEBUG: caller = %p\n", caller);
    */

    /* get func name */
    snprintf(cmd, STRMAX, "addr2line -f -s -e \"%s\" %p", exe, func);
    // printf("%s\n", cmd);

    FILE* fp = popen(cmd, "r");

    if (fp == NULL) {
        return;
    }

    fgets(func_name, STRMAX, fp);
    end_str(func_name);

    pclose(fp);

    /* get caller name and file */
    snprintf(cmd, STRMAX, "addr2line -f -s -e \"%s\" %p", exe, caller);
    // printf("%s\n", cmd);

    fp = popen(cmd, "r");

    if (fp == NULL) {
        return;
    }

    fgets(caller_name, STRMAX, fp);
    end_str(caller_name);
    fgets(caller_file, STRMAX, fp);
    end_str(caller_file);

    pclose(fp);
}

void
__attribute__((constructor))
trace_begin(void)
{
    /* get current executable path */
    readlink("/proc/self/exe", exe, STRMAX);
}

void
__cyg_profile_func_enter(void* func,  void* caller)
{
    get_addr(func, caller);

    fprintf(stderr, "\e[2m%s:%s(): %s()\e[0m\n", caller_file, caller_name,
            func_name);
    /* fprintf(stderr, "\e[2m%s:%s(): -> %s()\e[0m\n", caller_file, caller_name, func_name); */
}

/*
void
__cyg_profile_func_exit (void *func, void *caller)
{
    get_addr(func, caller);

    fprintf(stderr, "\e[2m%s:%s(): <- %s() | %p <- %p\e[0m\n", caller_file, caller_name, func_name);
}
*/
