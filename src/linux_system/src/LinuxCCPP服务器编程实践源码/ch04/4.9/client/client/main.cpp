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
#include <malloc.h>

#define BUF_LEN 250
typedef struct sockaddr_in SOCKADDR_IN;
typedef struct sockaddr SOCKADDR;


int main()
{
    int err;
    u_long argp;
    char szMsg[] = "Hello, server, I have received your message.";
    int sockClient = socket(AF_INET, SOCK_STREAM, 0);//新建一个套接字
    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //服务器的IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //服务器的监听端口
    err = connect(sockClient, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //向服务器发出连接请求
    if (-1 == err) //判断连接是否成功
    {
        printf("Failed to connect to the server:%d\n",errno);
        return 0;
    }
    char recvBuf[BUF_LEN];
    int i, cn = 1, iRes;

    int leftlen;
    unsigned char *pdata;

    iRes = recv(sockClient, (char*)&leftlen, sizeof(int), 0); //接收来自服务器的信息

    leftlen = ntohl(leftlen);
    printf("Need to receive %d bytes data.\n", leftlen);
    while (leftlen > BUF_LEN)
    {
        //接收来自服务器的信息，每次最大只能接收BUF_LEN个数据，具体接收多少未知
        iRes = recv(sockClient, recvBuf, BUF_LEN, 0);
        if (iRes > 0)
        {
            printf("\nNo.%d:Recv %d bytes:", cn++, iRes);
            for (i = 0; i < iRes; i++) //打印本次接收到的数据
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//对方关闭连接
            puts("\nThe server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return -1;
        }
        leftlen = leftlen - iRes;
    }
    if (leftlen > 0)
    {
        iRes = recv(sockClient, recvBuf, leftlen, 0);
        if (iRes > 0)
        {
            printf("\nNo.%d:Recv %d bytes:", cn++, iRes);
            for (i = 0; i < iRes; i++) //打印本次接收到的数据
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//对方关闭连接
            puts("\nThe server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return -1;
        }
        leftlen = leftlen - iRes;
    }

    char sendBuf[100];
    sprintf(sendBuf, "I'm the client. I've finished receiving the data.");//组成字符串
    send(sockClient, sendBuf, strlen(sendBuf) + 1, 0); //发送字符串给客户端
    memset(sendBuf, 0, sizeof(sendBuf));

    puts("Sending data to the server is completed");
    close(sockClient); //关闭套接字
    getchar();
    return 0;
}
