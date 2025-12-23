#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>

int main(int argc, char const *argv[])
{
    DIR* streamp;
    struct dirent *dep;
    if (argc < 2)
    {
        printf("please input directory\n");
        return 0;
    }
    streamp = opendir(argv[1]);
    errno = 0;
    while ((dep = readdir(streamp)) != NULL)
    {
        printf("Found file : %s\n", dep->d_name);
    }
    if (errno != 0)
    {
        printf("readdir error\n");
    }
    closedir(streamp);
    return 0;
}
