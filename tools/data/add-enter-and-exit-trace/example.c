#include <unistd.h>

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

    // infinite loop to keep the program running
    while(1) {
        sleep(1);
    }

    return 0;
}

