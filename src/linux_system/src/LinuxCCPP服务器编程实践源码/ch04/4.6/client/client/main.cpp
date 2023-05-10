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

#define BUF_LEN 300
typedef struct sockaddr_in SOCKADDR_IN;
typedef struct sockaddr SOCKADDR;
int main()
{

    int err;
    long argp;
    char szMsg[] = "Hello, server, I have received your message.";

    int sockClient = socket(AF_INET, SOCK_STREAM, 0);//新建一个套接字

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //服务器的IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //服务器的监听端口
    err = connect(sockClient, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //向服务器发出连接请求
    if (-1 == err) //判断连接是否成功
    {
        printf("Failed to connect to the server. Please check whether the server is started\n");
        getchar();
        return 0;
    }
    char recvBuf[BUF_LEN];
    int i, cn = 1, iRes;
    do
    {
        iRes = recv(sockClient, recvBuf, BUF_LEN, 0); //接收来自服务器的信息
        if (iRes > 0)
        {
            printf("\nRecv %d bytes:", iRes);
            for (i = 0; i < iRes; i++)
                printf("%c", recvBuf[i]);
            printf("\n");
        }
        else if (iRes == 0)//对方关闭连接
            puts("The server has closed the send connection.\n");
        else
        {
            printf("recv failed:%d\n", errno);
            close(sockClient);
            return 1;
        }

    } while (iRes > 0);
    //开始向客户端发送数据
    char sendBuf[100];
    for (i = 0; i < 10; i++)
    {
        sprintf(sendBuf, "N0.%d I'm the client,1+1=2\n", i + 1);//组成字符串
        send(sockClient, sendBuf, strlen(sendBuf) + 1, 0); //发送字符串给客户端
        memset(sendBuf, 0, sizeof(sendBuf));
    }
    puts("Sending data to the server is completed.");
    close(sockClient); //关闭套接字
    getchar();
    return 0;
}
