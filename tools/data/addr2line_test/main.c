#include <unistd.h>
#include <stdio.h>

static void foo2()
{
    // some code
}

void foo1()
{
    foo2();
}

void foo()
{
    // chdir("/home/shihyu");
    foo1();
}

int main(int argc, const char* argv[])
{
    foo();

    while(1) {
        sleep(10);
    }

    return 0;
}

