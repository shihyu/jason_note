#include <stdio.h>
#include <stdlib.h>

int main(int argc, char const *argv[])
{
    int *p = malloc(32);
    free(p);
    return 0;
}
