// winSend.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"
#include <iostream>


#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include "winsock2.h"
#pragma comment(lib, "ws2_32.lib")

#include <stdio.h>

char wbuf[50];

int main()
{
    int sockfd;
    int size;
    char on = 1;
    struct sockaddr_in saddr;
    int ret;

    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);

    WORD wVersionRequested;
    WSADATA wsaData;
    int err;

    wVersionRequested = MAKEWORD(2, 2); //制作Winsock库的版本号
    err = WSAStartup(wVersionRequested, &wsaData); //初始化Winsock库
    if (err != 0) return 0;

    //设置地址信息，ip信息
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(9999);
    saddr.sin_addr.s_addr = inet_addr("192.168.35.128");//该ip为服务端所在的ip

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);  //创建udp 的套接字
    if (sockfd < 0)
    {
        perror("failed socket");
        return -1;
    }
    //设置端口复用
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //发送信息给服务端
    puts("please enter data:");
    scanf_s("%s", wbuf, sizeof(wbuf));
    ret = sendto(sockfd, wbuf, sizeof(wbuf), 0, (struct sockaddr*)&saddr,
                 sizeof(struct sockaddr));
    if (ret < 0) perror("sendto failed");
    closesocket(sockfd);
    WSACleanup(); //释放套接字库
    return 0;
}

