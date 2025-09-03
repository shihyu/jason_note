#include <cstdio>
#include<sys/socket.h>
#include <arpa/inet.h>
#include<string.h>
#include <errno.h>

int main()
{
    int sfp;
    struct sockaddr_in s_add;
    unsigned short portnum = 10051;
    struct sockaddr_in serv = { 0 };
    char on = 1;
    int serv_len = sizeof(serv);
    int err;
    sfp = socket(AF_INET, SOCK_STREAM, 0);
    if (-1 == sfp)
    {
        printf("socket fail ! \r\n");
        return -1;
    }
    printf("socket ok !\n");
    printf("ip=%s,port=%d\n", inet_ntoa(serv.sin_addr), ntohs(serv.sin_port)); //打印没绑定前的地址
    setsockopt(sfp, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));//允许地址的立即重用
    memset(&s_add, 0, sizeof(struct sockaddr_in));
    s_add.sin_family = AF_INET;
    s_add.sin_addr.s_addr = inet_addr("192.168.0.117"); //这个ip地址必须是本机上有的
    s_add.sin_port = htons(portnum);

    if (-1 == bind(sfp, (struct sockaddr *)(&s_add), sizeof(struct sockaddr)))  //绑定
    {
        printf("bind fail:%d!\r\n", errno);
        return -1;
    }
    printf("bind ok !\n");
    getsockname(sfp, (struct sockaddr *)&serv, (socklen_t*)&serv_len); //获取本地套接字地址
    //打印套接字地址里的ip和端口值
    printf("ip=%s,port=%d\n", inet_ntoa(serv.sin_addr), ntohs(serv.sin_port));
    return 0;
}