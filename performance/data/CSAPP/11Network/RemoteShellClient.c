#include <unistd.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char const *argv[])
{
    struct in_addr ip;
    const char* loalhost = "127.0.0.1";
    int ret = inet_pton(AF_INET, loalhost, &ip);
    if (ret != 1)
    {
        printf("inet_pton failed\n");
        return 0;
    }
    struct sockaddr_in sock;
    sock.sin_family = AF_INET;
    sock.sin_port = 3455;
    sock.sin_addr = ip;
    // socket
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd == -1)
    {
        printf("socket failed\n");
        return 0;
    }
    // connect
    if (connect(fd, (struct sockaddr*)(&sock), sizeof(struct sockaddr_in)) == -1)
    {
        printf("connect failed\n");
        return 0;
    }
    // send input to server
    while (1)
    {
        printf(">");
        fflush(stdout);
        char buf[1024] = {};
        ssize_t size = read(STDIN_FILENO, buf, 1024);
        if (size > 0)
        {
            write(fd, buf, size);
        }
    }
    return 0;
}
