#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
char rbuf[50];

int main()
{
    int sockfd, size, ret;
    char on = 1;
    struct sockaddr_in saddr;
    struct sockaddr_in raddr;

    //设置地址信息，ip信息
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(9999);
    saddr.sin_addr.s_addr = inet_addr("192.168.0.153");

    //创建udp 的套接字
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket failed");
        return -1;
    }
    //设置端口复用
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //把接收端地址信息绑定到套接字上
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        perror("sbind failed");
        return -1;
    }
    int  val = sizeof(struct sockaddr);
    puts("waiting data");
    //阻塞等待发送端的消息
    ret = recvfrom(sockfd, rbuf, 50, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
    if (ret < 0)
        perror("recvfrom failed");
    printf("recv data :%s\n", rbuf); //打印收到的消息
    close(sockfd);//关闭udp套接字
    getchar();
    return 0;
}
