#include <cstdio>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main(int argc, char *argv[])
{
    unsigned short port = 8888;		// 本地端口
    char on = 1;
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);//1.创建tcp套接字
    if (sockfd < 0)
    {
        perror("socket");
        exit(-1);
    }
    //配置本地网络信息
    struct sockaddr_in my_addr;
    bzero(&my_addr, sizeof(my_addr));	  // 清空
    my_addr.sin_family = AF_INET;		  // IPv4
    my_addr.sin_port = htons(port);	  // 端口
    my_addr.sin_addr.s_addr = htonl(INADDR_ANY); // ip
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));//设置端口复用
    int err_log = bind(sockfd, (struct sockaddr*)&my_addr, sizeof(my_addr));//2.绑定
    if (err_log != 0)
    {
        perror("binding");
        close(sockfd);
        getchar();
        exit(-1);
    }
    err_log = listen(sockfd, 10);//3.监听，套接字变被动
    if (err_log != 0)
    {
        perror("listen");
        close(sockfd);
        exit(-1);
    }
    while (1) //主进程 循环等待客户端的连接
    {
        char cli_ip[INET_ADDRSTRLEN] = { 0 };
        struct sockaddr_in client_addr;
        socklen_t cliaddr_len = sizeof(client_addr);
        puts("Father process is waitting client...");
        // 取出客户端已完成的连接
        int connfd = accept(sockfd, (struct sockaddr*)&client_addr, &cliaddr_len);
        if (connfd < 0)
        {
            perror("accept");
            close(sockfd);
            exit(-1);
        }
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            _exit(-1);
        }
        else if (0 == pid) { //子进程 接收客户端的信息，并返回给客户端
            close(sockfd);   // 关闭监听套接字，这个套接字是从父进程继承过来
            char recv_buf[1024] = { 0 };
            int recv_len = 0;
            // 打印客户端的 ip 和端口
            memset(cli_ip, 0, sizeof(cli_ip)); // 清空
            inet_ntop(AF_INET, &client_addr.sin_addr, cli_ip, INET_ADDRSTRLEN);
            printf("----------------------------------------------\n");
            printf("client ip=%s,port=%d\n", cli_ip, ntohs(client_addr.sin_port));
            // 接收数据
            while ((recv_len = recv(connfd, recv_buf, sizeof(recv_buf), 0)) > 0)
            {
                printf("recv_buf: %s\n", recv_buf); // 打印数据
                send(connfd, recv_buf, recv_len, 0); // 给客户端回数据
            }

            printf("client_port %d closed!\n", ntohs(client_addr.sin_port));
            close(connfd);    //关闭已连接套接字
            exit(0); //子进程结束
        }
        else if (pid > 0)      // 父进程
            close(connfd);    //关闭已连接套接字
    }
    close(sockfd);
    return 0;
}