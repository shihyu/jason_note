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

#define BUF_LEN 300
typedef struct sockaddr_in SOCKADDR_IN;
typedef struct sockaddr SOCKADDR;

struct MyData
{
    int nLen;
    char data[0];
};

int main()
{
    int err, i, iRes;

    int sockSrv = socket(AF_INET, SOCK_STREAM, 0); //创建一个套接字，用于监听客户端的连接

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118");
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000);  //使用端口8000

    bind(sockSrv, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //绑定
    listen(sockSrv, 5); //监听

    SOCKADDR_IN addrClient;
    int cn = 0, len = sizeof(SOCKADDR);
    struct MyData *mydata;
    while (1)
    {
        printf("--------wait for client-----------\n");
        //从连接请求队列中取出排在最前的一个客户端请求，如果队列为空就就阻塞
        int sockConn = accept(sockSrv, (SOCKADDR*)&addrClient, (socklen_t*)&len);
        printf("--------client comes-----------\n");
        cn = 5550; //总共要发送5550字节的消息体，这个长度是发送端设定的，没和接收端约好

        mydata = (MyData*)malloc(sizeof(MyData) + cn);
        mydata->nLen = htonl(cn); //整型数据要转为网络字节序
        memset(mydata->data, 'a', cn);
        mydata->data[cn - 1] = 'b';
        send(sockConn, (char*)mydata, sizeof(MyData) + cn, 0); //发送全部数据给客户端
        free(mydata);

        //发送结束，开始接收客户端发来的信息
        char recvBuf[BUF_LEN];

        // 持续接收客户端数据，直到对方关闭连接
        do {

            iRes = recv(sockConn, recvBuf, BUF_LEN, 0);
            if (iRes > 0)
            {
                printf("\nRecv %d bytes:", iRes);
                for (i = 0; i < iRes; i++)
                    printf("%c", recvBuf[i]);
                printf("\n");
            }
            else if (iRes == 0)
                printf("\nThe client has closed the connection.\n");
            else
            {
                printf("recv failed with error: %d\n", errno);
                close(sockConn);
                return 1;
            }

        } while (iRes > 0);

        close(sockConn); //关闭和客户端通信的套接字
        puts("Continue monitoring?(y/n)");
        char ch[2];
        scanf("%s", ch, 2); //读控制台两个字符，包括回车符
        if (ch[0] != 'y') //如果不是y就退出循环
            break;
    }
    close(sockSrv); //关闭监听套接字
    return 0;
}
