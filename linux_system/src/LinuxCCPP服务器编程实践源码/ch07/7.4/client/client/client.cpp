
#include "pch.h"
#include <stdio.h>
#include <winsock.h>
#pragma comment(lib,"wsock32")

#define  BUF_SIZE  200
#define PORT 8888
char wbuf[50], rbuf[100];
int main()
{
    char   buff[BUF_SIZE];
    SOCKET  s;
    int    len;
    WSADATA  wsadata;

    struct hostent *phe;      /*host information     */
    struct servent *pse;      /* server information  */
    struct protoent *ppe;     /*protocol information */
    struct sockaddr_in saddr;   /*endpoint IP address  */
    int   type;

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
    s = socket(PF_INET, SOCK_STREAM, 0);
    if (s == INVALID_SOCKET)
    {
        printf(" creat socket error \n");
        WSACleanup();
        return -1;
    }
    if (connect(s, (struct sockaddr *)&saddr, sizeof(saddr)) == SOCKET_ERROR)
    {
        printf("connect socket  error \n");
        WSACleanup();
        return -1;
    }
    printf("please enter data:");
    scanf_s("%s", wbuf, sizeof(wbuf));
    len = send(s, wbuf, sizeof(wbuf), 0);
    if (len < 0) perror("send failed");
    len = recv(s, rbuf, sizeof(rbuf), 0);
    if (len < 0) perror("recv failed");
    printf("server reply:%s\n", rbuf);

    closesocket(s);
    WSACleanup();
    return 0;
}
