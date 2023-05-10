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
    int err, i, iRes;
    char on = 1;
    int sockSrv = socket(AF_INET, SOCK_STREAM, 0); //创建一个套接字，用于监听客户端的连接
    assert(sockSrv >= 0);
    //允许地址的立即重用
    setsockopt(sockSrv, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    SOCKADDR_IN addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118");
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000);  //使用端口8000

    bind(sockSrv, (SOCKADDR*)&addrSrv, sizeof(SOCKADDR)); //绑定
    listen(sockSrv, 5); //监听

    SOCKADDR_IN addrClient;
    int cn = 0, len = sizeof(SOCKADDR);

    while (1)
    {
        printf("--------wait for client-----------\n");
        //从连接请求队列中取出排在最前的一个客户端请求，如果队列为空就就阻塞
        int sockConn = accept(sockSrv, (SOCKADDR*)&addrClient, (socklen_t*)&len);
        char sendBuf[111] = "";
        printf("--------client comes-----------\n");
        for (cn = 0; cn < 50; cn++)
        {
            memset(sendBuf, 'a', 111);
            if (cn == 49)
                sendBuf[110] = 'b'; //让最后一个字符为'b',这样看起来清楚一点
            send(sockConn, sendBuf, 111, 0); //发送字符串给客户端
        }
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
                printf("The client closes the connection.\n");
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
