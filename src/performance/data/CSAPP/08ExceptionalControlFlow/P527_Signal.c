#include <signal.h>
#include <stdio.h>
#include <unistd.h>

// type Ctrl+C from keyboard will enter this function
void interrupt_from_keyboard(int n)
{
    printf("SIGINT from keyboard\n");
}

int main(int argc, char const *argv[])
{
    signal(SIGINT, interrupt_from_keyboard);
    sleep(10);
    return 0;
}
