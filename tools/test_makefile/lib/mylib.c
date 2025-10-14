#include <stdio.h>
#include "mylib.h"

void hello_from_lib(const char* name) {
    printf("Hello %s from mylib!\n", name);
}

int add_numbers(int a, int b) {
    return a + b;
}
