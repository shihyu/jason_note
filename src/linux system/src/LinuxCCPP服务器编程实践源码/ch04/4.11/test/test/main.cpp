#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/ioctl.h>

int main()
{
    int err,s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);//创建流套接字
    if (s == -1) {
        printf("Error at socket()\n");
        return -1;
    }
    int su = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP); //创建数据报套接字
    if (s == -1) {
        printf("Error at socket()\n");
        return -1;
    }

    int optVal;
    int optLen = sizeof(optVal);
    //获取流套接字接收缓冲区大小
    if (getsockopt(s, SOL_SOCKET, SO_RCVBUF, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
        printf("Size of stream socket receive buffer: %ld bytes\n", optVal);
    //获取流套接字发送缓冲区大小
    if (getsockopt(s, SOL_SOCKET, SO_SNDBUF, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
        printf("Size of streaming socket send buffer: %ld bytes\n", optVal);

    //获取数据报套接字接收缓冲区大小
    if (getsockopt(su, SOL_SOCKET, SO_RCVBUF, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
        printf("Size of datagram socket receive buffer: %ld bytes\n", optVal);
    //获取数据报套接字发送缓冲区大小
    if (getsockopt(su, SOL_SOCKET, SO_SNDBUF, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
        printf("Size of datagram socket send buffer:%ld bytes\n", optVal);

    getchar();
    return 0;
}
