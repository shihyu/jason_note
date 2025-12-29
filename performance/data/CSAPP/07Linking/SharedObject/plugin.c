#include <stdio.h>
extern void func();

void hello()
{
    printf("hello\n");
    func();
}