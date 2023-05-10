// client.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"
#include <stdio.h>
#include <winsock.h>
#pragma comment(lib,"wsock32")

#define  BUF_SIZE  200
#define PORT 8888
char wbuf[50], rbuf[100];
int main()
{
    SOCKET  s;
    int    len;
    WSADATA  wsadata;
    struct hostent *phe;      /*host information     */
    struct servent *pse;      /* server information  */
    struct protoent *ppe;     /*protocol information */
    struct sockaddr_in saddr,raddr;   /*endpoint IP address  */
    int fromlen,ret,type;
    if (WSAStartup(MAKEWORD(2, 0), &wsadata) != 0)
    {
        printf("WSAStartup failed\n");
        WSACleanup();
        return -1;
    }
    memset(&saddr, 0, sizeof(saddr));
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(PORT);
    saddr.sin_addr.s_addr = inet_addr("192.168.0.153");

    /**** get protocol number  from protocol name  ****/
    if ((ppe = getprotobyname("UDP")) == 0)
    {
        printf("get protocol information error \n");
        WSACleanup();
        return -1;
    }
    s = socket(PF_INET, SOCK_DGRAM, ppe->p_proto);
    if (s == INVALID_SOCKET)
    {
        printf(" creat socket error \n");
        WSACleanup();
        return -1;
    }
    fromlen = sizeof(struct sockaddr);
    printf("please enter data:");
    scanf_s("%s", wbuf, sizeof(wbuf));
    ret = sendto(s, wbuf, sizeof(wbuf), 0, (struct sockaddr*)&saddr,sizeof(struct sockaddr));
    if (ret < 0) perror("sendto failed");
    len = recvfrom(s, rbuf, sizeof(rbuf), 0, (struct sockaddr*)&raddr,&fromlen);
    if(len < 0) perror("recvfrom failed");
    printf("server reply:%s\n", rbuf);

    closesocket(s);
    WSACleanup();
    return 0;
}
