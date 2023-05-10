#include <cstdio>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
int main()
{
    int err;
    int  sockClient = socket(AF_INET, SOCK_STREAM, 0);//新建一个套接字
    char msg[] = "hi,server"; //要发送给服务器端的消息
    sockaddr_in addrSrv;
    addrSrv.sin_addr.s_addr = inet_addr("192.168.0.118"); //服务器的IP
    addrSrv.sin_family = AF_INET;
    addrSrv.sin_port = htons(8000); //服务器的监听端口
    err = connect(sockClient, (struct sockaddr *)&addrSrv, sizeof(struct sockaddr)); //向服务器发出连接请求
    if (-1 == err) //判断连接是否成功
    {
        printf("Failed to connect to the server.Please check whether the server is started\n");
        return 0;
    }
    char recvBuf[100];
    recv(sockClient, recvBuf, 100, 0); //接收来自服务器的信息
    printf("receive server's msg:%s\n", recvBuf); //打印收到的信息
    send(sockClient, msg, strlen(msg) + 1, 0); //向服务器发送信息
    close(sockClient); //关闭套接字
    getchar();

    return 0;
}
