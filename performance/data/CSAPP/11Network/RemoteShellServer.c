#include <unistd.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/types.h>

int main()
{
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    if (listenfd == -1)
    {
        printf("socket failed\n");
        return 0;
    }
    // 127.0.0.1 to int IPV4 address
    struct in_addr ip;
    const char* loalhost = "127.0.0.1";
    int ret = inet_pton(AF_INET, loalhost, &ip);
    if (ret != 1)
    {
        printf("inet_pton failed\n");
        return 0;
    }
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(struct sockaddr_in));
    addr.sin_family = AF_INET;
    addr.sin_port = 3455;
    addr.sin_addr = ip;
    if (bind(listenfd, (struct sockaddr*)(&addr), sizeof(struct sockaddr_in)) == -1)
    {
        printf("bind failed\n");
        return 0;
    }
    if (listen(listenfd, 50) == -1)
    {
        printf("listen failed\n");
        return 0;
    }
    struct sockaddr_in clientaddr;
    socklen_t len = sizeof(struct sockaddr_in);
    int connectfd = accept(listenfd, (struct sockaddr*)&clientaddr, &len);
    if (connectfd == -1)
    {
        printf("accept failed\n");
        return 0;
    }
    else
    {
        printf("accept success\n");
    }
    // deal with incoming connection
    char buf[1024] = {};
    ssize_t size = 0;
    while ((size = read(connectfd, buf, 1024)) != -1)
    {
        if (size > 0)
        {
            char line[1024] = {};
            memset(line, 0, 1024);
            strncpy(line, buf, size);
            write(STDOUT_FILENO, line, size);
        }
        sleep(1);
    }
    return 0;
}
