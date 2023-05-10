#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
char rbuf[50], sbuf[100];
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
    saddr.sin_port = htons(8888);
    saddr.sin_addr.s_addr = htonl(INADDR_ANY);

    //创建udp 的套接字
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        puts("socket failed");
        return -1;
    }
    //设置端口复用
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    //绑定地址信息，ip信息
    ret = bind(sockfd, (struct sockaddr*)&saddr, sizeof(struct sockaddr));
    if (ret < 0)
    {
        puts("sbind failed");
        return -1;
    }
    int  val = sizeof(struct sockaddr);

    while (1)  //循环接收客户端发来的消息
    {
        puts("waiting data");
        ret = recvfrom(sockfd, rbuf, 50, 0, (struct sockaddr*)&raddr, (socklen_t*)&val);
        if (ret < 0) perror("recvfrom failed");
        printf("recv data :%s\n", rbuf);
        sprintf(sbuf,"server has received your data(%s)\n", rbuf);
        ret = sendto(sockfd, sbuf, strlen(sbuf), 0, (struct sockaddr*)&raddr, sizeof(struct sockaddr));
        memset(rbuf, 0, 50);
    }
    //关闭udp套接字
    close(sockfd);
    getchar();
    return 0;
}
