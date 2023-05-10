#include <stdio.h>
#include <jemalloc/jemalloc.h>
//define to jemalloc
#define malloc(size) je_malloc(size)
#define calloc(count,size) je_calloc(count,size)
#define realloc(ptr,size) je_realloc(ptr,size)
#define free(ptr) je_free(ptr)

int main(void)
{
    char* pcon;

    pcon = malloc(10 * sizeof(char));

    if (!pcon) {
        fprintf(stderr, "malloc failed!\n");
    }

    if (pcon != NULL) {
        free(pcon);
        pcon = NULL;
    }

    fprintf(stderr, "main end!\n");
    return 0;
}

