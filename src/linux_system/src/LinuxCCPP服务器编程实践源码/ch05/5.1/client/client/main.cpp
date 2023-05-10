#include <cstdio>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
char wbuf[50];
int main()
{
    int sockfd, size, ret;
    char on = 1;
    struct sockaddr_in saddr;
    size = sizeof(struct sockaddr_in);
    memset(&saddr, 0, size);

    //设置接收端的地址信息
    saddr.sin_family = AF_INET;
    saddr.sin_port = htons(9999); //注意这个是接收端的端口
    saddr.sin_addr.s_addr = inet_addr("192.168.0.153");//这个ip是虚拟机的ip

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);  //创建udp 的套接字
    if (sockfd < 0)
    {
        perror("failed socket");
        return -1;
    }
    //设置端口复用
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    puts("please enter data:");
    scanf("%s", wbuf, sizeof(wbuf)); //输入要发送的信息
    ret = sendto(sockfd, wbuf, sizeof(wbuf), 0, (struct sockaddr*)&saddr,
                 sizeof(struct sockaddr)); //发送信息给接收端
    if (ret < 0) 	perror("sendto failed");
    close(sockfd);
    getchar();
    return 0;
}
