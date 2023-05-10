#include <cstdio>
#include <assert.h>
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
    int err;
    int s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); //创建流套接字
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
    //获取套接字s的类型
    if (getsockopt(s, SOL_SOCKET, SO_TYPE, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
    {
        if (SOCK_STREAM == optVal) // SOCK_STREAM宏定义值为1
            printf("The current socket is a stream socket.\n"); //当前套接字是流套接字
        else if (SOCK_DGRAM == optVal) // SOCK_ DGRAM宏定义值为2
            printf("The current socket is a datagram socket.\n");//当前套接字是数据报套接字
    }
    //获取套接字su的类型
    if (getsockopt(su, SOL_SOCKET, SO_TYPE, (char*)&optVal, (socklen_t *)&optLen) == -1)
        printf("getsockopt failed:%d", errno);
    else
    {
        if (SOCK_STREAM == optVal)  // SOCK_STREAM宏定义值为1
            printf("The current socket is a stream socket.\n");
        else if (SOCK_DGRAM == optVal) // SOCK_ DGRAM宏定义值为2
            printf("The current socket is a datagram socket.\n");
    }
    getchar();
    return 0;
}
